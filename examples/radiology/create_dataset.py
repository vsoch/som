#!/bin/env python

# A dataset in this scope is a collection of tables in BigQuery
# Our default is a group called stanford under som-langlotz-lab
# (complete address is som-langlotz-lab:stanford) and so these
# were the steps to first create that collection of tables. We
# would want to do the equivalent given adding another 
# institution data, etc.

from som.data.google.radiology import Client
from som.data.google.bigquery import (
    get_dataset
    set_dataset_metadata
)

# A client holds an auth to bigquery.
client = Client()
bigquery_client = client.bq
dataset = get_dataset(bigquery_client) #default is stanford

description = '''This is the metadata table for Stanford 
              Medicine radiology, including metadata for images 
              and text that are stored as objects in Google Storage.'''
friendly_name = "Stanford Medicine Images and Text Metadata"

# Now we will update the metadata for it!
dataset = set_dataset_metadata(dataset=dataset,
                               description=description,
                               friendly_name=friendly_name)
