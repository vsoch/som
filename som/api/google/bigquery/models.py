'''
google/modals.py: models for datastore

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

from som.api.google.storage.validators import (
    validate_model
)

from som.api.google.utils import get_google_service
from .utils import (
    get_bucket,
    upload_file
)

import google.cloud.datastore as datastore
import google.cloud.bigquery as bq

from retrying import retry
from som.api.google.storage.datastore import (
    get_key_filters,
    parse_keys
)

from google.cloud.exceptions import (
    BadRequest,
    GrpcRendezvous
)
from som.logger import bot
import datetime
import collections
import sys
import os


################################################################################
# Bases
################################################################################

class BatchManager:
    '''a batch manager is bucket to hold multiple objects to filter, query, etc.
    It a way to compile a set, and then run through a transaction. It is intended
    to be a Base class for the DataStoreBatch and BigQueryBatch
    '''
    def __init__(self,client=None):
        self.client = client
        self.tasks = []
        self.queries = []

    def get(self):
        raise NotImplementedError

    def add(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def runInsert(self):
        raise NotImplementedError
       
    def runQueries(self):
        raise NotImplementedError

    def query(self):
        raise NotImplementedError



class ModelBase:

    def __init__(self,client=None):
        self.client = client

    def update_fields(self):
        return NotImplementedError

    def get_or_create(self):
        return NotImplementedError

    def setup(self):
        return NotImplementedError

    def save(self):
        return NotImplementedError

    def create(self):
        return NotImplementedError

    def delete(self):
        return NotImplementedError

    def update_or_create(self):
        return NotImplementedError

    def update(self):
        return NotImplementedError

    def get(self):
        return NotImplementedError


################################################################################
# BigQuery Batch Manager
################################################################################

        
class BigQueryManager(BatchManager):
    '''a batch manager that sends metadata to Google BigQuery
    '''
    def __init__(self, **kwargs):
        super(BigQueryManager, self).__init__(**kwargs)
        if self.client is None:
            self.client = bigquery.Client()


class BigQueryBase:

    def __init__(self,client=None):
        self.client = client

    def update_fields(self):
        return NotImplementedError

    def get_or_create(self):
        return NotImplementedError

    def setup(self):
        return NotImplementedError

    def save(self):
        return NotImplementedError

    def create(self):
        return NotImplementedError

    def delete(self):
        return NotImplementedError

    def update_or_create(self):
        return NotImplementedError

    def update(self):
        return NotImplementedError

    def get(self):
        return NotImplementedError


