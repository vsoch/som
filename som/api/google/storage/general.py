#!/usr/bin/env python

'''
general.py: general models for text and images

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
    


def image(uid,entity,url):
    '''image returns an image object. entity is the parent
    '''
    fields = [{'key':'uid','required':True,'value': uid},
              {'key':'url','required':True,'value': url}]

    collection = entity.collection.get_name()
    entity = entity.get_name()

    model = {'fields':fields,
             'exclude_from_indexes': ['url'],
             'key':['Collection', collection, 'Entity',entity,'Image', uid]}

    return model
    


def text(uid,entity,url):
    '''text returns a text object. entity is the parent
    '''
    fields = [{'key':'uid','required':True,'value':uid},
              {'key':'url','required':True,'value':url}]

    collection = entity.collection.get_name()
    entity = entity.get_name()

    model =  {'fields':fields,
              'key':['Collection', collection, 'Entity',entity,'Text', uid]}
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
            self.update_or_create(client,fields=fields)
        else:
            self.update_or_create(client,
                                  fields=fields,
                                  save=False)
        

    def collection(self,client):
        '''collection will return the collection associated with
        the entity
        '''
        return client.get(collection.key)


    def images(self,client):
        '''images will return images associated with the entity
        '''
        key = self.get_keypath()
        return client.get(client.key(*key, "Image"))
    

    def text(self,client):
        '''text will return text associated with the entity
        '''
        key = self.get_keypath()
        return client.get(client.key(*key, "Text"))


class Image(ModelBase):

    def __init__(self,client,uid,entity,url,create=True,fields=None):
        self.entity = entity
        self.model = image(uid=uid,entity=entity,url=url)
        super(Image, self).__init__(client)
        if create:
            self.update_or_create(client,fields=fields)
        else:
            self.update_or_create(client,
                                  fields=fields,
                                  save=False)


class Text(ModelBase):

    def __init__(self,client,uid,entity,url,create=True,fields=None):
        self.entity = entity
        self.model = text(uid=uid,entity=entity,url=url)
        super(Text, self).__init__(client)
        if create:
            self.update_or_create(client,fields=fields)
        else:
            self.update_or_create(client,
                                  fields=fields,
                                  save=False)



######################################################################################
# Radiology Client to interact with Models
######################################################################################


class Client(ClientBase):

    def __init__(self,bucket_name,**kwargs):
        self.bucket_name = bucket_name
        self.batch = BatchManager()
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

    def create_image(self,uid,entity,url,create=True,fields=None):
        return Image(client=self.datastore,
                     uid=uid,
                     entity=entity,
                     url=url,
                     create=create,
                     fields=fields)


    def create_text(self,uid,url,entity,create=True,fields=None):
        return Text(client=self.datastore, 
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

    def upload_text(self,text,entity,batch=True):
        '''upload_text will add a text object to the batch manager'''

        uid = self.get_storage_path(text,entity)
        bucket_folder = self.get_storage_path(text,entity,return_folder=True)

        text_obj = self.upload_object(file_path=text,
                                      bucket_folder=bucket_folder)

        url = "https://storage.googleapis.com/%s/%s" %(self.bucket['name'],
                                                       text_obj['name'])

        new_text = self.create_text(uid=uid,
                                    entity=entity,
                                    url=url,
                                    create=not batch)

        bot.logger.debug('TEXT: %s',new_text)

        if batch:
            self.batch.add(new_text)
        return new_text


    def upload_image(self,image,entity,batch=True):
        '''upload_images will add an image object to the batch manager
        '''
        bucket_folder = self.get_storage_path(image,entity,return_folder=True)

        image_obj = self.upload_object(file_path=image,
                                       bucket_folder=bucket_folder)

        url = "https://storage.googleapis.com/%s/%s" %(self.bucket['name'],
                                                       image_obj['name'])
                                                    
        fields = {'storage':image_obj,
                  'download':image_obj['mediaLink']}

        new_image = self.create_image(uid=image_obj['id'],
                                      entity=entity,
                                      url=url,
                                      fields=fields,
                                      create=not batch)

        bot.logger.debug('IMAGE: %s',new_image)

        if batch:
            self.batch.add(new_image)

        return new_image


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
            entity.update(client=self.datastore,
                          fields=metadata)
       
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
            self.batch.insert(client=self.datastore)
