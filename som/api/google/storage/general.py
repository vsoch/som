#!/usr/bin/env python

'''
general.py: general models for text and images

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

from som.api.google.storage.client import ClientBase
from som.api.google.storage.models import *
from som.api.google.storage.utils import *
from som.logger import bot
from som.utils import read_json
import six

######################################################################################
# Specs and base data structures for a general model
######################################################################################


def entity(uid,collection):
    '''entity returns an entity object
    parent is a collection
    '''
    fields = [{'key':'uid','required':True,'value':uid}]

    if type(collection) not in six.string_types:
        collection = collection.get_name()
    model = {'fields':fields,
             'key':['Collection',collection,'Entity', uid]}

    return model



def collection(uid):
    '''entity returns an entity object
    parent is an owner
    '''
    fields = [{'key':'uid','required':True,'value':uid}]

    model = {'fields':fields,
             'key':['Collection', uid]}
    return model
    


def storageObject(uid,entity,url,storage_type):
    '''image returns an image object. entity is the parent
    '''
    fields = [{'key':'uid','required':True,'value': uid},
              {'key':'url','required':True,'value': url}]

    collection = entity.collection.get_name()
    entity = entity.get_name()

    storage_type = storage_type.replace(' ','-').lower().capitalize()

    model = {'fields':fields,
             'exclude_from_indexes': ['url'],
             'key':['Collection', collection, 'Entity',entity, storage_type, uid]}

    return model
    


######################################################################################
# Core Models, extending base model
######################################################################################


class Collection(ModelBase):
  
    def __init__(self,client,uid,create=True,fields=None):
        self.model = collection(uid=uid)
        super(Collection, self).__init__(client)
        if create:
            self.update_or_create(fields=fields)
        else:
            self.update_or_create(fields=fields,
                                  save=False)


class Entity(ModelBase):

    def __init__(self,client,collection,uid,create=False,fields=None):
        self.collection = collection
        self.model = entity(uid,collection)
        super(Entity, self).__init__(client)
        if create:
            self.update_or_create(fields=fields)
        else:
            self.update_or_create(fields=fields,
                                  save=False)
        

class Object(ModelBase):

    def __init__(self,client,uid,entity,url,object_type,create=True,fields=None):
        self.entity = entity
        self.model = storageObject(uid=uid,entity=entity,url=url,storage_type=object_type)
        super(Object, self).__init__(client)
        if create:
            self.update_or_create(fields=fields)
        else:
            self.update_or_create(fields=fields,
                                  save=False)



######################################################################################
# Client to interact with Models
######################################################################################


class Client(ClientBase):

    def __init__(self,bucket_name,**kwargs):
        self.bucket_name = bucket_name
        super(Client, self).__init__(**kwargs)
    
    def __str__(self):
        return "storage.google.%s" %self.bucket_name

    def __repr__(self):
        return "storage.google.%s" %self.bucket_name



    ###################################################################
    ## Create #########################################################
    ###################################################################

    def create_collection(self,uid,create=True,fields=None):
        return Collection(client=self.datastore,
                          uid=uid,
                          create=create,
                          fields=fields)


    def create_entity(self,collection,uid,create=True,fields=None):
        return Entity(client=self.datastore,
                      collection=collection,
                      uid=uid,
                      create=create,
                      fields=fields)


    def create_object(self,uid,entity,url,object_type,create=True,fields=None):
        '''Object type should be one in Image or Text'''
        return Object(client=self.datastore,
                      object_type=object_type,
                      uid=uid,
                      entity=entity,
                      url=url,
                      create=create,
                      fields=fields)


    def create_object(self,uid,entity,url,object_type,create=True,fields=None):
        '''Object type should be one in Image or Text'''
        return Object(client=self.datastore,
                      object_type=object_type,
                      uid=uid,
                      entity=entity,
                      url=url,
                      create=create,
                      fields=fields)

    ###################################################################
    ## Get ############################################################
    ###################################################################

    def get_storage_path(self,file_path,entity,return_folder=False):
        folder = '/'.join(entity.get_keypath())
        bucket_path = "%s/%s" %(folder,os.path.basename(file_path))
        if return_folder:
            return os.path.dirname(bucket_path)
        return bucket_path


    def get_collections(self,uids=None,limit=None,keys_only=False):
        return self.batch.get(kind="Collection",
                              keys=uids,
                              limit=limit,
                              keys_only=keys_only)


    def get_entities(self,collection=None,field=None,uids=None,limit=None,keys_only=False):
        '''eg:     pmc_articles = client.get_entities(uids=pmc_keys,field="pmcid")
        '''  
        ancestor = None
        if collection is not None:
            ancestor = self.batch.client.key("Collection", collection) 
        return self.batch.get(kind="Entity",
                              limit=limit,
                              field=field,
                              ancestor=ancestor,
                              keys=uids,
                              keys_only=keys_only)


    def get_images(self,entity,limit=None,keys_only=False):
        return self.batch.query(kind="Image",
                                limit=limit,
                                keys_only=keys_only,
                                ancestor=entity.key)


    def get_text(self,entity,limit=None,keys_only=False):
        return self.batch.query(kind="Text",
                                limit=limit,
                                keys_only=keys_only,
                                ancestor=entity.key)

  
    ###################################################################
    ## Upload #########################################################
    ###################################################################

    def upload_object(self,file_path,entity,
                      object_type=None,
                      batch=True,
                      fields=None):

        '''upload_object will add a general object to the batch manager
        The object is uploaded to Google Storage, returning storage fields.
        If the user has provided additional fields, these are added to the
        call to create a new object (datastore)'''

        if object_type is None:
            bot.warning("You must specify object_type. Image or Text.")
            return None

        uid = self.get_storage_path(file_path,entity)
        bucket_folder = self.get_storage_path(file_path,entity,return_folder=True)

        storage_obj = self.put_object(file_path=file_path,
                                      bucket_folder=bucket_folder)

        # Obtain storage fields, update with provided fields
        storage_fields = get_storage_fields(storage_obj)
        if fields is not None:
            storage_fields.update(fields)
        fields = storage_fields

        url = "https://storage.googleapis.com/%s/%s" %(self.bucket['name'],
                                                       storage_obj['name'])

        new_object = self.create_object(uid=uid,
                                        entity=entity,
                                        url=url,
                                        fields=fields,
                                        object_type=object_type,
                                        create=not batch)

        if batch:
            self.batch.add(new_object)
        return new_object


    def upload_text(self,text,entity,batch=True,fields=None):
        '''upload_text will add a text object to the batch manager'''
        new_object = self.upload_object(file_path=text,
                                        entity=entity,
                                        fields=fields,
                                        object_type="Text",
                                        batch=batch)
        bot.debug('TEXT: %s' %new_object)
        return new_object


    def upload_image(self,image,entity,batch=True,fields=None):
        '''upload_images will add an image object to the batch manager
        '''
        new_object = self.upload_object(file_path=image,
                                        entity=entity,
                                        fields=fields,
                                        object_type="Image",
                                        batch=batch)
        bot.debug('IMAGE: %s' %new_object)
        return new_object


    def upload_dataset(self,uid,collection,
                       images=None,
                       texts=None,
                       entity_metadata=None,
                       images_metadata=None,
                       texts_metadata=None,
                       batch=True):

        '''upload takes a list of images, texts, and optional metadata
        and uploads to datastore (metadata) and storage (images)
        :param uid: should be the unique id for the entity, with one or more images/texts
        :param entity_metadata: a single dictionary of keys/values for the entity
        :param texts_metadata: a dictionary with keys corresponding to text paths
        of key value pairs for the text in question
        :param images_metadata: the same, but for images
        :param collection: should be the collection to add the entity to
        :param batch: add entities in batches (recommended, default True)
        '''

        if images_metadata is None: images_metadata = {}
        if texts_metadata is None: texts_metadata = {}

        # Add entity
        entity = self.create_entity(collection=collection,
                                    uid=uid)

        if entity_metadata is not None:
            entity.update(fields=entity_metadata)
       
        if texts is not None:

            for text in texts:
                fields = None

                # metadata provided for the text?
                if text in texts_metadata:
                    fields = texts_metadata[text]

                self.upload_text(text=text,
                                 entity=entity,
                                 fields=fields,
                                 batch=batch)



        if images is not None:
            for img in images:
                fields = None

                # metadata provided for the image?
                if img in images_metadata:
                    fields = images_metadata[img]

                self.upload_image(image=img,
                                  entity=entity,
                                  fields=fields,
                                  batch=batch)

        # Run a transaction for put (insert) images and text, and clears queue
        if batch:
            self.batch.runInsert()
