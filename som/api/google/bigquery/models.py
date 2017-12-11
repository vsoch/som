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
 
from google.cloud import bigquery
from som.api.google.models import BatchManager, ModelBase
from retrying import retry
from google.cloud.exceptions import (
    BadRequest,
    GrpcRendezvous
)
from som.logger import bot
import datetime
import sys
import os


class BigQueryManager(BatchManager):
    '''a batch manager that sends metadata to Google BigQuery, is a child
       class of som.google.api.models BatchManager that has skeleton functions
       to fill in for insert, run, etc.

        self.client = client
        self.tasks = []
        self.queries = []

       Parameters
       ==========
       rows: a list of rows to add to some table, to be specified when the 
       manager is initialized.

    '''
    def __init__(self, **kwargs):
        super(BigQueryManager, self).__init__(**kwargs)
        if self.client is None:
            self.client = bigquery.Client()
        self.rows = []
        self.table = None

    def set_table(self,table, clear_rows=True):
        self.table = table
        if clear_rows is True:
            bot.debug("Clearing previously added rows. Set clear_rows to False to prevent this.")
            self.rows = []
        return self.rows 


    def runInsert(self, table=None):
        if len(self.rows) > 0:
            table = table.insert_data(self.rows)
            self.rows = []
        return table
       

    def add_rows(self, rows, table=None):
         ''' Add one or more rows to a table. Rows should be a list of
             dict, each item corresponding to a key/value
         '''
         table = self._validate_table(table)
         if table is not None:
             rows = self._dict_to_rows(rows, table.schema)
             self.rows = self.rows + rows


    def _validate_table(self, table, schema_required=True):
        ''' ensure that the user has provided a table, with the following
            order of preference:

            1. First preference goes to table provided at runtime
            2. Second preference goes to BatchManager table
            3. If not found, fail

         Parameters
         ==========
         table (required) to validate
         schema_required: Does the table, if found, require a schema?

         Returns
         =======
         If valid, the valid table. If not, returns None

        '''

        # First preference to table provided at runtime
        active_table = table
        if active_table is None:
            active_table = self.table

        # Second (above) to BatchManagers, then error)
        if active_table is None:
            bot.error("Please provide a table to the Manager or function.") 
            return False

        # The table must have a schema
        if schema_required is True:
            if table.schema in ["",[]]: 
                bot.error("Table must be defined with a schema before batch insert.") 
                active_table = None

        return active_table


    def _dict_to_rows(self, rows, schema):
        ''' check a list of rows, each a dict of field names
            (keys) and values, against a schema. Only fields present in the
            schema are returned, and missing fields are returned empty.
        '''
        schema_fields = [x.name for x in schema]

        valid_rows = []
        if not isinstance(rows, list):
            rows = [rows]       
        for rowdict in rows:
            if isinstance(rowdict, dict):
                new_row = [ rowdict[key] if key in rowdict else None for key in schema_fields]
                if len(new_row) > 0:
                    unlisted = []
                    for item in new_row:
                        if isinstance(item,list):
                            item=','.join([str(x) for x in item])
                        unlisted.append(item)
                    valid_rows.append(unlisted)
        return valid_rows
