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

from google.cloud.exceptions import Forbidden
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
                      suid,
                      project,
                      bucket_name,
                      query_entity=True,
                      filters=None):

    '''
    show progress while downloading images for a Collection/[c]/Entity/study 
    
    Parameters
    ==========

    collection_name: the name of the collection, typically an IRB number
    output_folder: the base directory to create a study folder in
    project: Google Cloud project name
    suid: an suid of interest to query (eg, if querying an Entity, you would
          use the suid of the patient, an Image would be an suid of the
          study SUID --> (coded accession#)
    query_entity: by default, we query the entity first, and then get images.
                  to query the images (studies) set this to False.
    bucket_name: the name for the Google Storage Bucket (usually provided)
    filters: a list of tuples to apply to filter the query. Default is:

         [ ("entity_id","=", study) ]

    to retrieve all Image items that are equal to the study name

    Returns
    =======
    path to newly created image file

    '''

    if filters is None:
        if query_entity is True:
            filters = [ ("uid","=", suid) ]
        else:
            filters = [ ("AccessionNumber","=", suid) ]

    bot.info("Collecting available images...")

    # Retrieve bucket, datastore client, images
    try:
        storage_client = storage.Client()

    except DefaultCredentialsError:
        bot.error("We didn't detect your GOOGLE_APPLICATION_CREDENTIALS in the environment! Did you export the path?")
        sys.exit(1)
    except Forbidden:
        bot.error("The service account specified by GOOGLE_APPLICATION_CREDENTIALS does not have permission to use this resource.")
        sys.exit(1)

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    bucket = storage_client.get_bucket(bucket_name)
    client = retry_get_client(bucket_name,project)
    collection = retry_get_collection(client,collection_name)

    if query_entity is True:
        entity_set = retry_get_entity(client,filters)
        images = []
        for entity in entity_set:
            entity_images = client.get_images(entity=entity)
            images = [x for x in entity_images if x not in images]
    else:
        images = retry_get_images(client,filters)
    
    bot.info("Found %s images for suid %s in collection %s" %(len(images),
                                                             suid,
                                                             collection_name))
    
    progress = 0
    total = len(images)

    files = []
    if len(images) > 0:
        bot.debug("Saving images and metadata...")
        for image in images:

            # Download image
            file_name = prepare_folders(output_folder=output_folder,
                                        image_name = image.key.name)
            
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



def prepare_folders(output_folder,image_name):
    '''prepare download path for image, and return path.
    '''

    folders = image_name.split('/')[:-1] # last is the image
    image_name = image_name.split('/')[-1]
    for folder in folders:
        output_folder = "%s/%s" %(output_folder,folder)
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
 
    return "%s/%s" %(output_folder,image_name)



def download_collection(collection,
                        project,
                        suid,
                        bucket,
                        query_entity=True,
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
                             suid=suid,
                             collection_name=collection,
                             project=project,
                             query_entity=query_entity,
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
def retry_get_entity(client,filters):
    return client.batch.query(kind="Entity",
                              filters=filters)


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
