'''
google/utils.py: general storage utility functions

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


from googleapiclient.errors import HttpError
from googleapiclient import (
    http,
    discovery
)

from oauth2client.client import GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials

from som.logger import bot

from som.utils import (
    get_installdir,
    read_file,
    run_command
)

from subprocess import (
    Popen,
    PIPE,
    STDOUT
)

import tempfile
import zipfile

from glob import glob
import httplib2
import inspect
import imp
import os
import json
import pickle
import re
import requests
from retrying import retry
import shutil
import simplejson
import sys
import tempfile
import time
import zipfile


######################################################################################
# Testing/Retry Functions
######################################################################################

def stop_if_result_none(result):
    '''stop if result none will return True if we should not retry 
    when result is none, False otherwise using retrying python package
    '''
    do_retry = result is not None
    return do_retry


# Simple default retrying for calls to api
doretry = retry(wait_exponential_multiplier=1000,wait_exponential_max=10000,stop_max_attempt_number=10)



##########################################################################################
# GOOGLE GENERAL API #####################################################################
##########################################################################################

def get_google_service(service_type=None,version=None):
    '''
    get_url will use the requests library to get a url
    :param service_type: the service to get (default is storage)
    :param version: version to use (default is v1)
    '''
    if service_type == None:
        service_type = "storage"
    if version == None:
        version = "v1"

    credentials = GoogleCredentials.get_application_default()
    return discovery.build(service_type, version, credentials=credentials) 


##########################################################################################
# GOOGLE STORAGE API #####################################################################
##########################################################################################
    
def get_bucket(storage_service,bucket_name):
    req = storage_service.buckets().get(bucket=bucket_name)
    return req.execute()


def delete_object(storage_service,bucket_name,object_name):
    '''delete_file will delete a file from a bucket
    :param storage_service: the service obtained with get_storage_service
    :param bucket_name: the name of the bucket (eg singularity-hub)
    :param object_name: the "name" parameter of the object.
    '''
    try:
        operation = storage_service.objects().delete(bucket=bucket_name,
                                                     object=object_name).execute()
    except HttpError as e:
        pass
        operation = e
    return operation


def upload_file(storage_service,bucket,bucket_path,file_path,verbose=True):
    '''get_folder will return the folder with folder_name, and if create=True,
    will create it if not found. If folder is found or created, the metadata is
    returned, otherwise None is returned
    :param storage_service: the drive_service created from get_storage_service
    :param bucket: the bucket object from get_bucket
    :param file_path: the path to the file to upload
    :param bucket_path: the path to upload to
    '''
    if bucket_path[-1] != '/':
        bucket_path = "%s/" %(bucket_path)
    bucket_path = "%s%s" %(bucket_path,os.path.basename(file_path))
    body = {'name': bucket_path }

    # Create media object with correct mimetype
    mimetype = sniff_extension(file_path,verbose=verbose)
    media = http.MediaFileUpload(file_path,
                                 mimetype=mimetype,
                                 resumable=True)
    request = storage_service.objects().insert(bucket=bucket['id'], 
                                               body=body,
                                               predefinedAcl="publicRead",
                                               media_body=media)
    return request.execute()



def list_bucket(bucket,storage_service):
    # Create a request to objects.list to retrieve a list of objects.        
    request = storage_service.objects().list(bucket=bucket['id'], 
                                             fields='nextPageToken,items(name,size,contentType)')
    # Go through the request and look for the folder
    objects = []
    while request:
        response = request.execute()
        objects = objects + response['items']
    return objects


def get_image_path(repo_url,commit):
    '''get_image_path will determine an image path based on a repo url, removing
    any token, and taking into account urls that end with .git.
    :param repo_url: the repo url to parse:
    :param commit: the commit to use
    '''
    repo_url = repo_url.split('@')[-1].strip()
    if repo_url.endswith('.git'):
        repo_url =  repo_url[:-4]
    return "%s/%s" %(re.sub('^http.+//www[.]','',repo_url),commit)




#####################################################################################
# METADATA
#####################################################################################

def get_storage_fields(obj):
    '''get_storage_fields will return a subset of storage object
    fields, to be saved as strings with a datastore object.
    '''                                   
    fields = {'storage_bucket':obj['bucket'],
              'storage_md5Hash':obj['md5Hash'],
              'storage_updated':obj['updated'],
              'storage_download':obj['mediaLink'],
              'storage_metadataLink':obj['selfLink'],
              'storage_crc32c':obj['crc32c'],
              'storage_etag':obj['etag'],
              'storage_owner':obj['owner']['entity'],
              'storage_name':obj['name'],
              'storage_id':obj['id'],
              'storage_contentType':obj['contentType'],
              'storage_size':obj['size']}
    return fields


def get_metadata(key):
    '''get_metadata will return metadata about an instance from within it.
    :param key: the key to look up
    '''
    headers = {"Metadata-Flavor":"Google"}
    url = "http://metadata.google.internal/computeMetadata/v1/instance/attributes/%s" %(key)        
    response = api_get(url=url,headers=headers)

    # Successful query returns the result
    if response.status_code == 200:
        return response.text
    else:
        bot.error("Error retrieving metadata %s, returned response %s" %(key,
                                                                         response.status_code))
    return None



######################################################################################
# Extensions and Files
######################################################################################


def sniff_extension(file_path,verbose=True):
    '''sniff_extension will attempt to determine the file type based on the extension,
    and return the proper mimetype
    :param file_path: the full path to the file to sniff
    :param verbose: print stuff out
    '''
    mime_types =    { "xls": 'application/vnd.ms-excel',
                      "xlsx": 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      "xml": 'text/xml',
                      "ods": 'application/vnd.oasis.opendocument.spreadsheet',
                      "csv": 'text/plain',
                      "tmpl": 'text/plain',
                      "pdf":  'application/pdf',
                      "php": 'application/x-httpd-php',
                      "jpg": 'image/jpeg',
                      "png": 'image/png',
                      "gif": 'image/gif',
                      "bmp": 'image/bmp',
                      "txt": 'text/plain',
                      "doc": 'application/msword',
                      "js": 'text/js',
                      "swf": 'application/x-shockwave-flash',
                      "mp3": 'audio/mpeg',
                      "zip": 'application/zip',
                      "rar": 'application/rar',
                      "tar": 'application/tar',
                      "arj": 'application/arj',
                      "cab": 'application/cab',
                      "html": 'text/html',
                      "htm": 'text/html',
                      "default": 'application/octet-stream',
                      "folder": 'application/vnd.google-apps.folder',
                      "img" : "application/octet-stream" }

    ext = os.path.basename(file_path).split('.')[-1]

    mime_type = mime_types.get(ext,None)

    if mime_type == None:
        mime_type = mime_types['txt']

    if verbose==True:
        bot.info("%s --> %s" %(file_path,mime_type))

    return mime_type
