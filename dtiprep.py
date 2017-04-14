#!/usr/bin/env python
"""Run DTIPrep QC pipeline

Based heavily on qa-dtiprep.py (https://github.com/scitran-apps/qa-dtiprep/blob/master/qa-dtiprep.py)
"""
import os
import argparse
import glob
import logging
import sys
import subprocess
#import nibabel as nib

logging.basicConfig()
logger = logging.getLogger(__name__)


def __check_files(fileList):
    '''
    checks to see if files in fileList exist
    exits if not
    '''
    for filepath in fileList:
        if not os.path.isfile(filepath):
            msg = 'Failed finding input file:{}'.format(filepath)
            logger.error(msg)
            sys.exit(msg)


def __run_cmd(command):
    '''
    Wrapper for subprocess.call_check
    exits if return code is not 0
    '''
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        msg = 'Error: {} failed with exit code:{}'.format(e.cmd, e.returncode)
        logger.error(msg)
        sys.exit(msg)


# run the DTIPrep pipeline
def dtiprep(nrrdFile, protocol_file, outDir):
    command = ['DTIPrep',
               '-w', nrrdFile,
               '--returnparameterfile', os.path.join(outDir, 'params.txt'),
               '-c', '-p', protocol_file,
               '-f', outDir]

    __run_cmd(command)

    qcfile = os.path.abspath(glob.glob('{outDir}/*QC*nrrd'
                                       .format(outDir=outDir))[0])
    xmlfile = os.path.abspath(glob.glob('{outDir}/*QC*xml'
                                        .format(outDir=outDir))[0])

    return qcfile, xmlfile


def dwi_to_dti_estimate(inDir, stem):
    # Run DWIToDTIEstimation on DTIPrep QC'd files
    DWIVolume = os.path.join(inDir, stem + '_QCed.nrrd')
    DTIVolume = os.path.join(inDir, stem + '_QCed_DTI.nrrd')
    BaseVolume = os.path.join(inDir, stem + '_QCed_Baseline.nrrd')

    __check_files([DWIVolume, DTIVolume, BaseVolume])

    command = ['DWIToDTIEstimation',
               '--enumeration', 'WLS',
               '--shiftNeg',
               DWIVolume,
               DTIVolume,
               BaseVolume]

    __run_cmd(command)


def diffusion_weighted_volume_masking(inDir, stem):
    DWIVolume = os.path.join(inDir, stem + '_QCed.nrrd')
    BaseVolume = os.path.join(inDir, stem + '_QCed_Baseline.nrrd')
    MaskVolume = os.path.join(inDir, stem + '_MASK.nrrd')

    __check_files([DWIVolume, BaseVolume])

    command = ['DiffusionWeightedVolumeMasking',
               '--removeislands',
               DWIVolume,
               BaseVolume,
               MaskVolume]

    __run_cmd(command)


def tractography_label_map_seeding(inDir, stem):
    DTIVolume = os.path.join(inDir, stem + '_QCed_DTI.nrrd')
    MaskVolume = os.path.join(inDir, stem + '_MASK.nrrd')
    TractResult = os.path.join(inDir, stem + '_SlicerTractography.vtk')

    __check_files([DTIVolume])

    command = ['TractographyLabelMapSeeding',
               DTIVolume,
               TractResult,
               '--inputroi', MaskVolume,
               '--useindexspace',
               '--stoppingvalue 0.10']

    __run_cmd(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Run DTIPrep on a DTI File")
    parser.add_argument("scan", help="scan")
    parser.add_argument("--nrrdDir", dest="nrrdDir", help="nrrd directory")
    parser.add_argument("--outDir", dest="outDir", help="output directory")
    parser.add_argument("--metaDir", dest="metaDir", help="protocol directory")
    parser.add_argument("--protocolFile", dest="protocolFile", help="protocol file")
    args = parser.parse_args()

    if not args.nrrdDir:
        args.nrrdDir = '/input'
    if not args.outDir:
        args.outDir = '/output'
    if not args.metaDir:
        args.metaDir = '/meta'

    nrrdFile = os.path.join(args.nrrdDir, args.scan) + '.nrrd'
    #nrrdFile = dicom2nrrd(args.dicomDir,
    #                      args.outDir,
    #                      args.subject)
    if not os.path.isfile(nrrdFile):
        msg = 'Input:{} not found.'.format(nrrdFile)
        logger.error(msg)
        sys.exit(msg)

    # this is a bit messy but lets me check for a default protocol file
    # even when one is specified
    # useful for e.g. DBDC where 3 DTI scans have the same protocol
    # but are identified differently
    if not args.protocolFile:
        protocol_file = os.path.join(args.metaDir, 'dtiprep_protocol.xml')
    else:
        protocol_file = os.path.join(args.metaDir, args.protocolFile)

    if not os.path.isfile(protocol_file):
        if os.path.isfile(os.path.join(args.metaDir, 'dtiprep_protocol.xml')):
            protocol_file = os.path.join(args.metaDir, 'dtiprep_protocol.xml')
            logger.warning('Using default protocol_file:{}'
                           .format(protocol_file))
        else:
            msg = 'Input:{} not found.'.format(protocol_file)
            logger.error(msg)
            sys.exit(msg)

    qcfile, xmlfile = dtiprep(nrrdFile, protocol_file, args.outDir)
    dwi_to_dti_estimate(args.outDir, args.scan)
    diffusion_weighted_volume_masking(args.outDir, args.scan)
    tractography_label_map_seeding(args.outDir, args.scan)
