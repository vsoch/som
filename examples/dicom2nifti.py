#!/usr/bin/env python

# An example of using som-dicom

from som.dicom import (
   dicom2nifti,
   find_dicoms
)

import os

# Go to a directory with dicoms in subfolders
pwd = os.getcwd()

folders = find_dicoms(pwd)

# Save nifti to same folder as dicoms
outfiles = dicom2nifti(folders)

# Or save to custom output folder
output_folder = '/home/vanessa/Desktop'
outfiles = dicom2nifti(folders,output_folder)
