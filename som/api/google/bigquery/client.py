#!/usr/bin/env python

'''
client.py: simple client for google storage (images) and bigquery (metadata)
           Requires the environment variable GOOGLE_APPLICATION_CREDENTIALS

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

from .models import BigQueryManager
from som.api.google.storage.client import StorageClientBase
from som.api.google.storage.utils import get_storage_fields
from google.cloud import storage
from .utils import *
from .schema import dicom_schema
from som.logger import bot
import six


class BigQueryClient(StorageClientBase):
    ''' a BigQuery Client is a wrapper for Big Query and google Storage, with
        a general stratgy to upload to storage, and save metadata in BigQuery
        This client doesn't itself do batch uploads, but holds a class (batch)
        that handles calls from the user.
    '''

    def __init__(self, project, bucket_name, schema=None, **kwargs):
        super(BigQueryClient, self).__init__(project, bucket_name, **kwargs)
        self.bigquery = bigquery.Client(self.project)
        self.name = "bigquery"
        self.batch = BigQueryManager(client=self.bigquery)
        self.set_schema(schema)

    def set_schema(self, schema):
        if schema is None:
            schema = dicom_schema
        elif isinstance(schema, dict):
            schema = create_schema(schema)
        self.schema = schema


    def get_dataset(self, name):
        '''get a new dataset with "name" (required), returns
           None if doesn't exist
        '''
        return get_dataset(project=self.project,
                           client=self.bigquery,
                           name=name)


    def get_or_create_dataset(self, name):
        '''get a new dataset with "name" (required), creates if doesn't
           exist
        '''
        return create_dataset(project=self.project,
                              client=self.bigquery,
                              name=name)


    def get_table(self, table_name, dataset):
        '''get a table with "name" (required), returns
           None if doesn't exist
        '''
        return get_table(project=self.project,
                         client=self.bigquery,
                         table_name=table_name,
                         dataset=dataset)


    def get_or_create_table(self, dataset, table_name, quiet=False, schema=None):
        '''get a new table with "name" (required), creates if doesn't
           exist
        '''
        if schema is None:
            schema = self.schema
        return create_table(project=self.project,
                            client=self.bigquery,
                            schema=self.schema,
                            quiet=quiet,
                            dataset=dataset,
                            table_name=table_name)
 

    ###################################################################
    ## Get ############################################################
    ###################################################################

    def get_storage_path(self,table_name, 
                              file_path, 
                              entity_name, 
                              item_name):

        ''' get_storage_path will return the human readable path of a file
            in storage. It should look like:

            [ Bucket ] / [ Table ] / [ Entity    ] / [ Item ]           / [ images ]
            [ Bucket ] / [ IRB   ] / [ PatientID ] / [ AccessionNumber ]/ [ images ]

        '''        
        bucket_path = "%s/%s/%s/%s" %(table_name,
                                      entity_name,
                                      item_name,
                                      os.path.basename(file_path))
        return bucket_path


    def get_datasets(self, quiet=False):
        '''get a list of datasets, also prints to screen if not quiet'''
        bot.info("Datasets for project %s:" % self.project)
        datasets = list(self.bigquery.list_datasets())
 
        if not quiet:
            for dataset in datasets:
                print(dataset.name)
        return datasets
         

    def upload_item(self,
                    file_path,
                    item_id,
                    entity_id,
                    table_name,
                    permission=None,
                    mimetype=None):

        '''upload_item will take a file path, and upload the object to storage,
           fields and metadata are returned to update the item.
        '''
        # Retrieve storage path and folder in Google Storage
        uid = self.get_storage_path(file_path=file_path,
                                    item_name=item_id,
                                    table_name=table_name,
                                    entity_name=entity_id)

        bucket_folder = os.path.dirname(uid)

        # Returns none on httperror, if object already exists
        storage_obj = self.put_object(file_path=file_path,
                                      bucket_folder=bucket_folder,
                                      permission=permission,
                                      mimetype=mimetype)
        # We created it
        if storage_obj is None:
            return storage_obj

        fields = get_storage_fields(storage_obj)
        fields['url'] = "https://storage.googleapis.com/%s/%s" %(self.bucket['name'],
                                                                storage_obj['name'])
        return fields



    def upload_dataset(self, 
                       items,
                       table,
                       mimetype,
                       entity_key="entity_id",
                       item_key="item_id",
                       permission="projectPrivate",
                       metadata={},
                       batch=True):

        '''upload datasets will upload a number of items (a list of images) to 
        Google Storag, and if metadata is provided upload metadata to Google
        BigQuery. 
        :param table: a Google datastore table, defined with a schema that
                      matches the metadata
        :param metadata: a dictionary of dictionaries, the top level key
                         the names in the list of items, and each content
                         dictionary with key:value pairs of table_field:values
        :param entity_key: the keys to find the entity/item_name in the metadata. 
               item_key  : these keys are used to determine the path in storage
                          
                           / table / entity_id / item_id / file_paths

        :param batch: add entities in batches (recommended, default True)
        '''
       
        for item in items:

            if item in metadata:
                rowdict = metadata.get(item,{})
          
                # Entity and item keys must be provided for Storage path
                if entity_key in rowdict and item_key in rowdict:
                    entity_id = rowdict[entity_key]
                    item_id = rowdict[item_key]

                    # Get back storage fields
                    fields = self.upload_item(file_path=item,
                                              entity_id=entity_id,
                                              item_id=item_id,
                                              table_name=table.name,
                                              mimetype=mimetype,
                                              permission=permission)

                    if fields is not None:
                        rowdict.update(fields)
                    self.batch.add_rows(table=table, rows=[rowdict])

                else:
                    bot.warning("Skipping upload of %s, cannot determine storage path." %item)

        # Run batch insert of data to BigQuery
        if batch is True:
            return self.batch.runInsert(table)
