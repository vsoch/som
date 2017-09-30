#!/usr/bin/env python

'''
Storage client base, intended to be superclassed by DataStoreClient and
        BigQueryClient

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

from .utils import (
    get_bucket,
    upload_file
)
from som.api.google.utils import get_google_service
from som.api import ApiConnection
from som.logger import bot


class StorageClientBase(ApiConnection):
    ''' Connection to Google Storage, intended to be superclass
        of google.datastore.DataStoreClient and
           google.bigquery.BigQueryClient
    '''

    def __init__(self, project, bucket_name, **kwargs):
        super(ApiConnection, self).__init__(**kwargs)
        self.project = project
        self.storage = get_google_service('storage', 'v1')
        self.bucket_name = bucket_name

        if self.bucket_name is not None:
            self.get_bucket()

    def get_bucket(self):
        self.bucket = get_bucket(self.storage, self.bucket_name)

    def name(self):
        name = ""
        if self.bucket_name is not None:
            name = ".%s" %self.bucket_name
        return "google[%s][bigquery]%s" %(self.name,name)

    def __str__(self):
        return self.name()


    def put_object(self,bucket_folder,file_path, verbose=True,permission=None, mimetype=None):
        '''upload_object will upload a file to path bucket_path in storage
        '''
        return upload_file(storage_service=self.storage,
                           bucket=self.bucket,
                           mimetype=mimetype,
                           bucket_path=bucket_folder,
                           file_path=file_path,
                           permission=permission,
                           verbose=verbose)
