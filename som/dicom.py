#!/usr/bin/env python

'''

dicom.py: Helper functions for working with dicoms, not finished developing

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''


import dicom
import nibabel
import numpy
from glob import glob
import os
from som.logger import bot


def find_dicoms(folder,extension=None):
    '''find_dicoms will walk a directory structure and find dicoms in subfolders
    :param folder: the parent folder to look in
    :param extension: the extension to use. Default is .dcm
    '''
    folders = dict()

    if extension == None:
        extension = ".dcm"

    for dirpath, dirnames, filenames in os.walk(folder):
        dicoms = []
        for filename in [f for f in filenames if f.endswith(extension)]:
            dicoms.append(os.path.join(dirpath, filename))
        if len(dicoms) > 0:
            folders[dirpath] = dicoms
    bot.debug('Found %s directories with dicom.' %len(folders))
    return folders


def sniff_header(dicom_file):
    '''sniff_header will return an estimated affine, x,y,z dimension from
    the first image (or any) in a series of dicom
    '''
    header = dict()
    ds = dicom.read_file(dicom_file)
    header['xdim'] = ds.Rows
    header['ydim'] = ds.Columns
    header['window_center'] = int(ds.WindowCenter)
    return header
    

def read_series(dicoms,return_nifti=True):
    '''read_series will read in a series of dicoms belonging to a group
    :param dicoms: a list of dicom files to parse, assumed in same series and
    equal size
    :param return_nifti: If True (default) will turn image as Nifti File
    '''
    # Sort the dicoms
    dicoms.sort()

    # Get the size of the image
    params = sniff_header(dicoms[0])
    xdim = params['xdim']
    ydim = params['ydim']   
    windom_center = params['window_center']
 
    bot.debug("First dicom found with dimension %s by %s, using as standard." %(xdim,ydim))

    # Let's get ordering of images based on InstanceNumber
    ordered = dict()
    for d in range(len(dicoms)):    
        ds = dicom.read_file(dicoms[d])
        if ds.Rows == xdim and ds.Columns == ydim:
            ordered[int(ds.InstanceNumber)] = ds.pixel_array

    # Sort by order
    zdim = len(ordered)    
    data = numpy.ndarray((xdim,ydim,zdim))

    # Start at window center, then go back to zero
    index = 0
    for key in sorted(ordered.keys()):
        data[:,:,index] = ordered[key]
        index +=1
    
    if return_nifti == True:
        affine = numpy.diag((1,1,1,0))
        data = nibabel.Nifti1Image(data,affine=affine)
    return data


def dicom2nifti(folders,outdir=None,extension=None):
    '''dicom2nifti will take a list of folders and produce nifti files
    in an output directory. If not defined, they will be output in their
    original directory.
    '''
    if isinstance(folders,dict):
        folders = list(folders.keys())
    
    if not isinstance(folders,list):
        folders = [folders]

    outfiles = []
    for folder in folders:
        lookup = find_dicoms(folder,extension)
        for base,dicomlist in lookup.items():
            nii = read_series(dicomlist)
            if outdir != None:
                outfile = "%s/%s.nii.gz" %(outdir,os.path.basename(base))
            else:
                outfile = "%s/%s.nii.gz" %(base,os.path.basename(base))
            bot.info("Saving %s" %outfile)
            nibabel.save(nii,outfile)
            outfiles.append(outfile)
    return outfiles


if __name__ == '__main__':
    folder = os.getcwd()
    dicoms = find_dicoms(folder)
