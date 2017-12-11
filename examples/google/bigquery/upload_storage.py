#!/usr/bin/env python

# RADIOLOGY ---------------------------------------------------
# This is an example script to upload images to Google Storage
# and MetaData to BigQuery. Data MUST be de-identified

import os

# Start google storage client for pmc-stanford
from som.api.google.bigquery import BigQueryClient as Client
client = Client(bucket_name='radiology-test',
                project='som-langlotz-lab')

# Create/get BigQuery dataset
dataset = client.get_or_create_dataset('testing')

# Let's use the default dicom_schema
from som.api.google.bigquery.schema import dicom_schema

table = client.get_or_create_table(dataset=dataset,
                                   table_name='dicomCookies',
                                   schema=dicom_schema)

# Let's load some dummy data from deid
from deid.data import get_dataset
from deid.dicom import get_files
dicom_files = get_files(get_dataset('dicom-cookies'))

# Now de-identify to get clean files
from deid.dicom import get_identifiers, replace_identifiers
metadata = get_identifiers(dicom_files)
updated_files = replace_identifiers(dicom_files=dicom_files,
                                    ids=metadata)

# Define some metadata for each entity and item
updates = { "item_id" : "cookieTumorDatabase",
                        "entity_id":"cookie-47",
                        "Modality": "cookie"}

for image_file in dicom_files:
    if image_file in metadata:
        metadata[image_file].update(updates)
    else:
        metadata[image_file] = updates


# Upload the dataset
client.upload_dataset(items=dicom_files,
                       table=table,
                       mimetype="application/dicom",
                       entity_key="entity_id",
                       item_key="item_id",
                       metadata=metadata)
