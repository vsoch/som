'''
models.py: base models

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
    ''' A ModelBase is an empty shell to guide functions / actions that should
        be available for a model base subclass (eg, BigQuery or DataStore)
    '''

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


