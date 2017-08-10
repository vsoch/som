'''

Copyright (c) 2017 Vanessa Sochat, All Rights Reserved

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

from som.api.google.storage import Client
from som.utils import write_json
from som.logger import bot

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage
from retrying import retry

import tempfile
import os
import sys



try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request




def progress_download(collection_name,
                      output_folder,
                      study,
                      project,
                      bucket_name,
                      filters=None):

    '''
    show progress while downloading images for a Collection/[c]/Entity/study 
    
    Parameters
    ==========

    collection_name: the name of the collection, typically an IRB number
    output_folder: the base directory to create a study folder in
    project: Google Cloud project name
    study: the name of the study, usually an Entity SUID (coded accession#)
    bucket_name: the name for the Google Storage Bucket (usually provided)
    filters: a list of tuples to apply to filter the query. Default is:

         [ ("entity_id","=", study) ]

    to retrieve all Image items that are equal to the study name

    Returns
    =======
    path to newly created image file

    '''

    if filters is None:
        filters = [ ("entity_id","=", study) ]

    # Retrieve bucket, datastore client, images
    try:
        storage_client = storage.Client()
    except DefaultCredentialsError:
        bot.error("We didn't detect your GOOGLE_APPLICATION_CREDENTIALS in the environment! Did you export the path?")
        sys.exit(1)

    bucket = storage_client.get_bucket(bucket_name)
    client = retry_get_client(bucket_name,project)
    collection = retry_get_collection(client,collection_name)
    images = retry_get_images(client,filters)
    
    bot.info("Found %s images for study %s in collection %s" %(len(images),
                                                               study,
                                                               collection_name))
    
    progress = 0
    total = len(images)

    files = []
    if len(images) > 0:
        bot.debug("Saving images and metadata...")
        for image in images:

            # Download image
            file_name = "%s/%s" %(output_folder,image.key.name.replace('/','-'))
            blob = bucket.blob(image['storage_name'])

            bot.show_progress(progress, total, length=35)
            download_retry(blob,file_name)
            files.append(file_name)
            files.append(save_metadata(image,file_name))
            progress+=1
            bot.show_progress(progress,total,length=35)

        # Newline to finish
        sys.stdout.write('\n')

    return files


     
       
def save_metadata(image,file_name):
    '''
    save the image metadata to json "file_name", removing the created
    and updated timestamps from storage, to not confuse the user
    
    Parameters
    ==========
    image: a Google DataStore Entity that converts to dictionary
    file_name: the file name of the dicom the metadata is for

    Returns
    =======
    path to newly created image file

    '''
    metadata = dict(image)
    del metadata['created']
    del metadata['updated'] 
    metadata_file = file_name.replace('.dcm','.json')
    return write_json(metadata,metadata_file)



def download_collection(collection,
                        project,
                        study,
                        bucket,
                        output_folder=None,
                        filters=None):

    '''
    client function to download a collection in entirety, intended for
    command line application som get

    See parameters in progress_download
    '''

    if output_folder is None:
        output_folder = os.path.getcwd()

    if not os.path.exists(output_folder):
        bot.error("Output folder %s not found. Exiting." %output_folder)
        sys.exit(1)

    output_folder = "%s/%s" %(output_folder,collection)
    return progress_download(output_folder=output_folder,
                             study=study,
                             collection_name=collection,
                             project=project,
                             bucket_name=bucket,
                             filters=filters)



########################################################################
# RETRY FUNCTIONS
#----------------------------------------------------------------------
# exponential backoff for Google Cloud APIs that can have hiccups from
########################################################################


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
def retry_get_collection(client,collection_name):
    return client.create_collection(collection_name)

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
def retry_get_images(client,filters):
    return client.batch.query(kind="Image",
                                filters=filters)

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
def retry_get_client(bucket_name,project):
    return Client(bucket_name=bucket_name,
                  project_name=project)

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
def download_retry(blob,file_name):
    blob.download_to_filename(file_name)
