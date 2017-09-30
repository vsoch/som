'''
google/bigquery.py: bigquery general functions for client

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

https://googlecloudplatform.github.io/google-cloud-python/latest/bigquery/usage.html

'''

from google.cloud import bigquery
from som.logger import bot
import sys
import os

# Read in test dataset

def get_client(project=None, client=None):
    ''' return a new client if not provided, with project specified,
        or None to use the active project
    '''
    if client is None:
        client = bigquery.Client(project=project)
    return client


def list_datasets(project=None, client=None):
    '''print a list of datasets'''
    client = get_client(project, client)

    bot.info("Datasets for project %s:" % client.project)
    for dataset in client.list_datasets():
        print(dataset.name)


def get_dataset(name, project=None, client=None):
    ''' get a dataset. If doesn't exist, returns None
    '''
    client = get_client(project, client)
    dataset = client.dataset(name)
    if not dataset.exists():
        dataset = None
    return dataset


def create_schema(schema):
    ''' create a schema from a dictinoary, where keys are field values,
        and values are the type. Eg:
        {"Name":"STRING"}
    '''
    bqschema = []

    for field,field_type in schema.items():
        entry =     bigquery.SchemaField(field, field_type.upper()),
        bqschema.append(entry)
    return tuple(bqschema)


def create_table(dataset, table_name, project=None, schema=None, client=None, quiet=False):
    '''create a table for a specified dataset and project
    '''
    client = get_client(project, client)
    table = dataset.table(table_name)
    
    if not table.exists():
        if schema is None:
            bot.debug("Creating table with default dicom schema")
            from .schema import dicom_schema
            schema = dicom_schema

        # If user provides dict, create schema from it
        elif isinstance(schema, dict):
            schema = create_schema(schema)

        table.schema = schema
        table.create()
        message = 'Created table {} in dataset {}.'.format(table_name, dataset.name)
    else:
        message = 'Table {} in dataset {} already exists.'.format(table_name, dataset.name)

    if not quiet:
        bot.info(message)

    return table



def get_table(dataset, table_name, project=None, client=None):
    '''create a table for a specified dataset and project
    '''
    client = get_client(project, client)
    table = dataset.table(table_name)    
    if not table.exists():
        table = None
    return table


def create_dataset(name, project=None, client=None, quiet=False):
    '''create a new dataset with "name" (required) 
    '''
    client = get_client(project, client)

    # Name for dataset corresponds with IRB (our current "Collection" names)
    dataset = client.dataset(name)

    # Creates the new dataset
    message = ('Dataset {} already exists.').format(name)
    if not dataset.exists():
        dataset.create()
        message = ('Dataset {} created.').format(name)
    
    if not quiet:
        bot.info(message.format(dataset.name))
    return dataset
