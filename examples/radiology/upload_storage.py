#!/bin/env python

# This is an example script to upload data (images, text, metadata) to
# google cloud storage and datastore (for general data)


# GENERAL -----------------------------------------------------
# Here we are going to upload text and images from a general
# (non wordfish standard) format, specifically the compressed
# files served by pubmed open central for journal articles

import os
import tempfile
import tarfile
import imghdr
import urllib
from glob import glob
from som.api.google.storage.general import Client

general_client = Client(bucket_name='pmc')

# Here is the url for one tar.gz file, list at
# ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.txt
# oa_package/46/8e/PMC4283967.tar.gz	PLoS One. 2015 Jan 5; 10(1):e115691	PMC4283967	PMID:25559678	CC BY
download_file = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/46/8e/PMC4283967.tar.gz"
pmc_file = '%s/%s' %(tempfile.mkdtemp(),os.path.basename(download_file))
urllib.request.urlretrieve(download_file, pmc_file)
tmpdir = tempfile.mkdtemp()
tar = tarfile.open(pmc_file, "r:gz")
tar.extractall(tmpdir)
files = glob('%s/PMC4283967/*' %tmpdir)
images = [x for x in files if imghdr.what(x) is not None]
pdf_files = [x for x in files if x.lower().endswith('pdf')]        
xml_file = [x for x in files if x.lower().endswith('xml')][0]
images = images + pdf_files
with open(xml_file,'r') as filey:
    content = filey.read().strip('\n')

# At the end of our custom parsing we have metadata, images, and text
# content
# images
# metadata

# Create metadata and save with article
metadata = {"PMC":"PMC4283967",
            "PMID":"PMID:25559678",
            "TYPE":"article",
            "JOURNAL":"PLoS One."
            "PUBLICATED_DATE": "2015 Jan 5; 10(1):e115691",
            "DOWNLOAD_URL":"ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/46/8e/PMC4283967.tar.gz",
            "LICENSE":"CC BY"}

# 1) First we get a collection corresponding to the journal #TODO- shouldn't have spaces, caps, etc.
collection = general_client.get_collection(uid=metadata['JOURNAL'])

# 2) Generate entity (article)

# 3) Add images associated with entity

# 4) Add text associated with entity

# Add images, give collection, get

response = general_client.upload_dataset(structures)
