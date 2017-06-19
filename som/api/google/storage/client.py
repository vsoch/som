#!/usr/bin/env python

'''
client.py: simple clients for google storage. This first go uses
datastore for metadata, and Google Storage for images (objects) so
a client means a connection to both, with functions to interact with 
both. Both will look for the environment variable GOOGLE_APPLICATION_CREDENTIALS

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

import datetime

from google.cloud import datastore
from som.api.google.storage.utils import (
    get_google_service, 
    get_bucket,
    upload_file
)

from som.api.google.storage.models import BatchManager
from som.api import ApiConnection
from som.logger import bot


class ClientBase(ApiConnection):

    def __init__(self,**kwargs):
        super(ApiConnection, self).__init__(**kwargs)
        self.datastore = datastore.Client()
        self.batch = BatchManager(client=self.datastore)
        self.storage = get_google_service('storage', 'v1')
        if self.bucket_name is not None:
            self.get_bucket()
  
    def get_bucket(self):
        self.bucket = get_bucket(self.storage,self.bucket_name)

    def make_key(self,key,ancestor=None):
        if ancestor is not None:
            ancestor = list(ancestor.key._flat_path)
            key = ancestor + key
        return self.datastore.key(*key)


    def put_object(self,bucket_folder,file_path,verbose=True):
        '''upload_object will upload a file to path bucket_path in storage
        '''
        return upload_file(storage_service=self.storage,
                           bucket=self.bucket,
                           bucket_path=bucket_folder,
                           file_path=file_path,
                           verbose=verbose)
