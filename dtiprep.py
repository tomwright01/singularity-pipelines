#!/usr/bin/env python
"""Run DTIPrep QC pipeline

Based heavily on qa-dtiprep.py (https://github.com/scitran-apps/qa-dtiprep/blob/master/qa-dtiprep.py)
"""
import os
import argparse
import glob
import nibabel as nib


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


#Extract the b0 volumes to create a brainmask
def makemask(niiFile, bvalFile, outFile):
    with open(bvalFile, 'rb') as f:
        bvals = f.readline()
        bvals = [int(v) for v in bvals.strip().split(' ')]
    bZeros = [i for i, v in enumerate(bvals) if v == 0]

    niiFile = nib.load(niiFile)
    nii_bzeros = niiFile.get_data()[:, :, :, bZeros]
    mask_nii = nib.Nifti1Image(nii_bzeros, niiFile.affine, niiFile.header)
    nib.save(mask_nii, outFile)


# run the DTIPrep pipeline
def dtiprep(nrrdFile, maskFile, outDir):
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
    parser.add_argument("scan", help="scan")
    parser.add_argument("--nrrdDir", dest="nrrdDir", help="nrrd directory")
    parser.add_argument("--outDir", dest="outDir", help="output directory")
    args = parser.parse_args()

    if not args.nrrdDir:
        args.nrrdDir = '/input'
    if not args.outDir:
        args.outDir = '/output'

    nrrdFile = os.path.join(args.nrrdDir, args.scan) + '.nrrd'
    #nrrdFile = dicom2nrrd(args.dicomDir,
    #                      args.outDir,
    #                      args.subject)
    bvalFile = os.path.join(args.niiDir, args.scan) + '.bval'
    qcfile, xmlfile = dtiprep(nrrdFile, maskFile, args.outDir)
