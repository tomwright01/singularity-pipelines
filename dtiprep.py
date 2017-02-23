#!/usr/bin/env python
"""Run DTIPrep QC pipeline

Based heavily on qa-dtiprep.py (https://github.com/scitran-apps/qa-dtiprep/blob/master/qa-dtiprep.py)
"""
import os
import argparse
import glob


# Convert dicom to nrrd
def dicom2nrrd(dicomDir, nrrdDir, name):
    outName = name + '.nrrd'
    command = ('DWIConvert '
               '--inputDicomDirectory {dicomDir} '
               '--outputVolume {outName} '
               '--outputDirectory {outDir}').format(dicomDir=dicomDir,
                                                    outName=outName,
                                                    outDir=nrrdDir)
    os.system(command)
    return os.path.abspath('{outDir}/{outName}'.format(outDir=nrrdDir,
                                                       outName=outName))


# run the DTIPrep pipeline
def dtiprep(nrrdFile, outDir):
    command = ('DTIPrep '
               '-w {nrrdFile} '
               '--returnparameterfile {outDir}/params.txt '
               '-c -d -p default.xml '
               '-f {outDir}').format(nrrdFile=nrrdFile,
                                     outDir=outDir)
    os.system(command)

    qcfile = os.path.abspath(glob.glob('{outDir}/*QC*nrrd'
                                       .format(outDir=outDir))[0])
    xmlfile = os.path.abspath(glob.glob('{outDir}/*QC*xml'
                                        .format(outDir=outDir))[0])

    return qcfile, xmlfile

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Run DTIPrep on a DTI File")
    parser.add_argument("nrrdFile", help="nrrdFile")
    parser.add_argument("--nrrdDir", dest="nrrdDir", help="nrrd directory")
    parser.add_argument("--outDir", dest="outDir", help="output directory")
    args = parser.parse_args()

    if not args.nrrdDir:
        args.nrrdDir = '/input'
    if not args.outDir:
        args.outDir = '/output'

    nrrdFile = os.path.join(args.nrrdDir, args.nrrdFile)
    #nrrdFile = dicom2nrrd(args.dicomDir,
    #                      args.outDir,
    #                      args.subject)
    qcfile, xmlfile = dtiprep(nrrdFile, args.outDir)
