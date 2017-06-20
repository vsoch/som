#!/usr/bin/env python

# RADIOLOGY ---------------------------------------------------
# This is an example script to upload data (images, text, metadata) to
# google cloud storage and datastore. Data MUST be de-identified

import os

# Start google storage client for pmc-stanford
from som.api.google.storage import Client
client = Client(bucket_name='radiology')
collection = client.create_collection(uid='IRB41449')

# Let's load some dummy data from deid
from deid.data import get_dataset
from deid.dicom import get_files
dicom_files = get_files(get_dataset('dicom-cookies'))

# Now de-identify to get clean files
from deid.dicom import get_identifiers, replace_identifiers
ids=get_identifiers(dicom_files)
updated_files = replace_identifiers(dicom_files=dicom_files,
                                    ids=ids)

# Define some metadata for the entity
metadata = { "source_id" : "cookieTumorDatabase",
             "id":"cookie-47",
             "Modality": "cookie"}

# Upload the dataset
client.upload_dataset(images=updated_files,
                      collection=collection,
                      uid=metadata['id'],
                      entity_metadata=metadata)

# Now try with adding metadata for an image
images_metadata = {
                    updated_files[0]:
                           
                              {
                               "Modality":"cookie",
                               "Type": "chocolate-chip",
                               "Width": 350,
                               "Height": 350
                              }
                   }

# And again do the call
client.upload_dataset(images=updated_files,
                      collection=collection,
                      uid="cookie-47",
                      images_metadata=images_metadata)
