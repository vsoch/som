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
from som.logman import bot
from som.utils import read_json
import six

######################################################################################
# Specs and base data structures for each radiology model
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
            self.update_or_create(client,fields=fields)
        else:
            self.update_or_create(client,
                                  fields=fields,
                                  save=False)


class Entity(ModelBase):

    def __init__(self,client,collection,uid,create=True,fields=None):
        self.collection = collection
        self.model = entity(uid,collection)
        super(Entity, self).__init__(client)
        if create:
            self.update_or_create(fields=fields)
        else:
            self.update_or_create(fields=fields,
                                  save=False)
        
     #TODO: need to write these functions to work with right references
     # to client
    def collection(self):
        '''collection will return the collection associated with
        the entity
        '''
        return self.client.get(self.collection.key)


    def images(self):
        '''images will return images associated with the entity
        '''
        key = self.get_keypath()
        return self.client.get(client.key(*key, "Image"))
    

    def text(self):
        '''text will return text associated with the entity
        '''
        key = self.get_keypath()
        return self.client.get(self.client.key(*key, "Text"))



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
# Radiology Client to interact with Models
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
    ## Create and get #################################################
    ###################################################################

    def get_collection(self,uid,create=True,fields=None):
        return Collection(client=self.datastore,
                          uid=uid,
                          create=create,
                          fields=fields)


    def get_entity(self,collection,uid,create=True,fields=None):
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


    def get_storage_path(self,file_path,entity,return_folder=False):
        folder = '/'.join(entity.get_keypath())
        bucket_path = "%s/%s" %(folder,os.path.basename(file_path))
        if return_folder:
            return os.path.dirname(bucket_path)
        return bucket_path



    ###################################################################
    ## Upload #########################################################
    ###################################################################

    def upload_object(self,file_path,entity,object_type=None,batch=True):
        '''upload_object will add a general object to the batch manager'''

        if object_type is None:
            bot.logger.warning("You must specify object_type. Image or Text.")
            return None

        uid = self.get_storage_path(file_path,entity)
        bucket_folder = self.get_storage_path(file_path,entity,return_folder=True)

        storage_obj = self.put_object(file_path=file_path,
                                      bucket_folder=bucket_folder)

        fields = get_storage_fields(storage_obj)
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


    def upload_text(self,text,entity,batch=True):
        '''upload_text will add a text object to the batch manager'''
        new_object = self.upload_object(file_path=text,
                                        entity=entity,
                                        object_type="Text",
                                        batch=batch)
        bot.logger.debug('TEXT: %s',new_object)
        return new_object


    def upload_image(self,image,entity,batch=True):
        '''upload_images will add an image object to the batch manager
        '''
        new_object = self.upload_object(file_path=image,
                                        entity=entity,
                                        object_type="Image",
                                        batch=batch)
        bot.logger.debug('IMAGE: %s',new_object)
        return new_object


    def upload_dataset(self,uid,collection,images=None,texts=None,metadata=None,batch=True):
        '''upload takes a list of images, texts, and optional metadata 
        and uploads to datastore (metadata) and storage (images)
        :param uid: should be the unique id for the entity, with one or more images/texts
        :param collection: should be the collection to add the entity to
        :param batch: add entities in batches (recommended, default True)
        '''
                
        # Add entity
        entity = self.get_entity(collection=collection,
                                 uid=uid)

        if metadata is not None:
            entity.update(fields=metadata)
       
        if texts is not None:
            for text in texts:
                self.upload_text(text=text,
                                 entity=entity,
                                 batch=batch)

        if images is not None:
            for img in images:
                self.upload_image(image=img,
                                  entity=entity,
                                  batch=batch)

        # Run a transaction for put (insert) images and text, and clears queue
        if batch:
            self.batch.insert()
