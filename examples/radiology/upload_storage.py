#!/bin/env python

# This is an example script to upload data (images, text, metadata) to
# google cloud storage and datastore. We use the wordfish standard,
# assuming the data has been de-identified.

from som.storage.google.radiology import Client
from som.wordfish.structures import structure_dataset

compressed_data = '../../../wordfish-standard/demo/cookies.zip'
structures = structure_dataset(compressed_data)

client = Client()
response = client.upload(structures)
