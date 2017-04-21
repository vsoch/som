#!/usr/bin/env python

# This is an example script to upload data (images, text, metadata) to
# google cloud storage and datastore (for general data)

# Preparation of Pubmed Open Access Data

ftp_base = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc"
file_list = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.txt"

from glob import glob
import requests
import signal
import xmltodict
import imghdr
import tempfile
import shutil
import tarfile
import numpy
import urllib
import pandas
import os
import re
import pwd

######################################################################
# Pubmed Functions
######################################################################


def get_userhome():
    '''get userhome gets the user's home based on the uid,
    and NOT the environment variable which is not consistent'''
    return pwd.getpwuid(os.getuid())[5]


def get_pubmed(download_base=None):
    '''retrieve pubmed database, either from locally saved file,
    or if not yet generated, obtain from FTP server
    '''
    if download_base is None:
        download_base = get_userhome()
    output_file = '%s/pmc.tsv' %(download_base)
    if not os.path.exists(output_file):
        download_folder = tempfile.mkdtemp()
        pmc_file = '%s/pmc.txt' %download_folder
        urllib.request.urlretrieve(file_list, pmc_file)
        pmc = pandas.read_csv(pmc_file,sep="\t",skiprows=1,header=None)
        pmc.columns = ["TARGZ_FILE","JOURNAL","PMCID","PMID","LICENSE"]
        pmc.to_csv(output_file,sep="\t",index=None)
        return pmc
    return pandas.read_csv(output_file,sep="\t")


def read_file(file_path):
    with open (file_path, "r") as myfile:
        return myfile.read().replace('\n', '')

def read_xml(xml_file):
    with open(xml_file) as fd:
        return xmltodict.parse(fd.read())

def format_name(name):
    '''format name will ensure that all collection names have
    periods removed, lowercase, and spaces replaced with -
    I'm not sure if this is best, but it's safer than allowing anything
    '''
    return name.replace('.','').lower().replace(" ",'-')


def get_metadata(row):
    '''get_uid will return the metadata for a row, with the uid corresponding
    first to the PMID, and the PMC id if that is not defined
    '''
    pmid = row[1].PMID
    if not isinstance(pmid,str):
        if numpy.isnan(pmid):
            pmid = row[1].PMCID
    download_url = "%s/%s" %(ftp_base,row[1].TARGZ_FILE)
    metadata = {"pmcid":row[1].PMCID,
                "type":"article",
                "uid":pmid,
                "publication_date": publication_date,
                "download_url":download_url,
                "license":row[1].LICENSE}
    if not isinstance(row[1].PMID,str):
        if not numpy.isnan(row[1].PMID):
            metadata['pmid'] = row[1].PMID
    return metadata



def create_article(metadata):
    tmpdir = tempfile.mkdtemp()
    pmc_file = '%s/article.tar.gz' %(tmpdir)
    print('Downloading: %s' %(metadata['uid']))
    urllib.request.urlretrieve(metadata['download_url'], pmc_file)
    tar = tarfile.open(pmc_file, "r:gz")
    tar.extractall(tmpdir)
    files = glob('%s/%s/*' %(tmpdir,metadata['pmcid']))
    images = [x for x in files if imghdr.what(x) is not None]
    pdf_files = [x for x in files if x.lower().endswith('pdf')]        
    xml_file = [x for x in files if x.lower().endswith('xml')]
    images = images + pdf_files
    general_client.upload_dataset(images=images,
                                  texts=xml_file,
                                  collection=collection,
                                  uid=metadata['uid'],
                                  metadata=metadata)
    shutil.rmtree(tmpdir)
     

######################################################################
# Signals 
######################################################################


def signal_handler(signum, frame):
    raise Exception("Timed out!")

# Only allow each paper a 30 seconds to download
signal.signal(signal.SIGALRM, signal_handler)


######################################################################
# Preparation of Pubmed Open Access Data
######################################################################

import os
import tempfile
import tarfile
import imghdr
import urllib
from glob import glob

# Obtain 1.5 million pmc articles
pmc = get_pubmed()

# Start google storage client for pmc-stanford
from som.api.google.storage.general import Client
general_client = Client(bucket_name='pmc-stanford')

for row in pmc.iterrows():
        journal_name = row[1].JOURNAL
        date_match = re.search("\d{4}",journal_name)
        publication_date = journal_name[date_match.start():]
        journal_name = format_name(journal_name[:date_match.start()].strip())
        collection = general_client.get_collection({"uid":journal_name})
        metadata = get_metadata(row)
        article = create_article(metadata)

