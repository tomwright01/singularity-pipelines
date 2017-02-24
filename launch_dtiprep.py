#!/usr/bin/env python
"""Launch the DTIPrep pipeline"""

import datman.config
import datman.utils
import logging
import argparse
import os
import tempfile
import sys
import subprocess
import socket

CONTAINER = '/projects/twright/bootstrap_qa.img'

JOB_TEMPLATE = """
#####################################
#$ -S /bin/bash
#$ -wd /tmp/
#$ -N {name}
#$ -e {errfile}
#$ -o {logfile}
#####################################
echo "------------------------------------------------------------------------"
echo "Job started on" `date`
echo "------------------------------------------------------------------------"
{script}
echo "------------------------------------------------------------------------"
echo "Job ended on" `date`
echo "------------------------------------------------------------------------"
"""

logging.basicConfig(level=logging.WARN,
                    format="[%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class QJob(object):
    def __init__(self, cleanup=True):
        self.cleanup = cleanup

    def __enter__(self):
        self.qs_f, self.qs_n = tempfile.mkstemp(suffix='.qsub')
        return self

    def __exit__(self, type, value, traceback):
        try:
            os.close(self.qs_f)
            if self.cleanup:
                os.remove(self.qs_n)
        except OSError:
            pass

    def run(self, code, name="job", logfile="output.$JOB_ID", errfile="error.$JOB_ID", cleanup=True, slots=1):
        open(self.qs_n, 'w').write(JOB_TEMPLATE.format(script=code,
                                                       name=name,
                                                       logfile=logfile,
                                                       errfile=errfile,
                                                       slots=slots))
        logger.info('Submitting job')
        subprocess.call('qsub < ' + self.qs_n, shell=True)


def make_job(src_dir, dst_dir, nrrd_name, cleanup=True):
    # create a job file from template and use qsub to submit
    code = ("singularity run -B {src_dir}:/input -B {dst_dir}:/output {container} {nrrd_name}"
            .format(src_dir=src_dir,
                    dst_dir=dst_dir,
                    container=CONTAINER,
                    nrrd_name=nrrd_name))

    with QJob() as qjob:
        logfile = '{}:/tmp/output.$JOB_ID'.format(socket.gethostname())
        errfile = '{}:/tmp/error.$JOB_ID'.format(socket.gethostname())
        qjob.run(code=code, logfile=logfile, errfile=errfile)


def process_nrrd(src_dir, dst_dir, nrrd_file):
    scan, ext = os.path.splitext(nrrd_file)

    # expected name for the output file
    out_file = os.path.join(dst_dir, scan + '_QCed' + ext)
    if os.path.isfile(out_file):
        logger.info('File:{} already processed, skipping.'
                    .format(nrrd_file))
        return
    make_job(src_dir, dst_dir, nrrd_file)


def process_session(src_dir, out_dir, session):
    """Launch DTI prep on all nrrd files in a directory"""
    src_dir = os.path.join(src_dir, session)
    out_dir = os.path.join(out_dir, session)
    nrrds = [f for f in os.listdir(src_dir) if f.endswith('.nrrd')]

    # Who knew, not all nrrd files are DTI's
    nrrd_dti = []
    for f in nrrds:
        try:
            _, tag, _, _ = datman.scanid.parse_filename(f)
        except datman.scanid.ParseException:
            continue

        if 'DTI' in tag:
            nrrd_dti.append(f)

    if not nrrd_dti:
        logger.warning('No DTI nrrd files found for session:{}'.format(session))
        return
    logger.info('Found {} DTI nrrd files.'.format(len(nrrd_dti)))
    if not os.path.isdir(out_dir):
        try:
            os.mkdir(out_dir)
        except OSError:
            logger.error('Failed to create output directory:{}'
                         .format(out_dir))
            return

    for nrrd in nrrd_dti:
        process_nrrd(src_dir, out_dir, nrrd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Run DTIPrep on a DTI File")
    parser.add_argument("study", help="Study")
    parser.add_argument("--session", dest="session", help="Session identifier")
    parser.add_argument("--outDir", dest="outDir", help="output directory")
    args = parser.parse_args()

    cfg = datman.config.config(study=args.study)

    nrrd_path = cfg.get_path('nrrd')
    pipeline_path = cfg.get_path('dtiprep')

    if not os.path.isdir(pipeline_path):
        logger.info("Creating output path:{}".format(pipeline_path))
        os.mkdir(pipeline_path)

    if not os.path.isdir(nrrd_path):
        logger.error("Src directory:{} not found".format(nrrd_path))
        sys.exit(1)

    if not args.session:
        sessions = [os.path.join(nrrd_path, d) for d
                    in os.listdir(nrrd_path)
                    if os.path.isdir(os.path.join(nrrd_path, d))]
    else:
        sessions = [args.session]

    for session in sessions:
        process_session(nrrd_path, pipeline_path, session)
