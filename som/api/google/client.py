#!/usr/bin/env python

'''
client.py: Exposes combined clients for Google Storage, Datastore/BigQuery
           These functions are intended for batch uploads of images to storage
           and metadata elsewhere.
           All look for the environment variable GOOGLE_APPLICATION_CREDENTIALS

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

from som.logger import bot


def Client(project=None, bucket_name=None, use_bigquery=True):
    '''get a client, default returns bigquery + storage, optionally can use
       datastore
    '''

    if use_bigquery is False:
        from som.api.google.datastore import DataStoreClient
        client = DataStoreClient(project=project, bucket_name=bucket_name)

    #else:
    #    from som.api.google.bigquery import BigQueryClient
    #    client = BigQueryClient(project=project, bucket_name=bucket_name)

    return client
