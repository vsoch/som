#!/usr/bin/env python

'''
base.py: base module for working with som api

'''

from som.storage.google.client import ClientBase
from som.storage.google.models import *
from som.storage.google.utils import *
from som.logman import bot
from som.utils import read_json
from som.wordfish.structures import structure_dataset
import six

######################################################################################
# Specs and base data structures for each radiology model
######################################################################################


def entity(uid,collection,metadata=None):
    '''entity returns an entity object
    parent is a collection
    '''
    fields = [{'key':'uid','required':True,'value':uid},
              {'key':'metadata','required':False,'value':metadata}]

    if type(collection) not in six.string_types:
        collection = collection.get_name()
    model = {'fields':fields,
             'key':['Collection',collection,'Entity', uid]}

    return model



def collection(uid,description=None,metadata=None):
    '''entity returns an entity object
    parent is an owner
    '''
    fields = [{'key':'uid','required':True,'value':uid},
              {'key':'description','required':False,'value':description},
              {'key':'metadata','required':False,'value':metadata}]

    model = {'fields':fields,
             'exclude_from_indexes': ['metadata','description'],
             'key':['Collection', uid]}
    return model
    


def image(uid,entity,download,url,storage,description=None,metadata=None):
    '''image returns an image object. entity is the parent
    '''
    fields = [{'key':'uid','required':True,'value':uid},
              {'key':'description','required':False,'value':description},
              {'key':'metadata','required':False,'value':metadata},
              {'key':'download','required':True,'value':download,
               'key':'url','required':True,'value': url,
               'key':'storage','required':True,'value': storage}]

    # Likely the entity passed was an som.wordfish.radiology.Entity
    if type(entity) not in six.string_types:
        entity = entity.get_name()

    model = {'fields':fields,
             'exclude_from_indexes': ['storage','download','url'],
             'key':['Entity',entity,'Image', uid]}
    return model
    


def text(uid,entity,content,description=None,metadata=None):
    '''text returns a text object. entity is the parent
    '''
    fields = [{'key':'uid','required':True,'value':uid},
              {'key':'description','required':False,'value':description},
              {'key':'metadata','required':False,'value':metadata},
              {'key':'content','required':True,'value':content}]

    # Likely the entity passed was an som.wordfish.radiology.Entity
    if type(entity) not in six.string_types:
        entity = entity.get_name()

    model =  {'fields':fields,
              'exclude_from_indexes': ['storage','download','url'],
              'key':['Entity',entity,'Text', uid]}
    return model




######################################################################################
# Core Models, extending base model
######################################################################################


class Collection(ModelBase):
  
    def __init__(self,client,uid,create=True,**kwargs):
        self.model = collection(uid=uid)
        super(Collection, self).__init__(client,**kwargs)
        if create:
            self.this = self.update_or_create(client)


class Entity(ModelBase):

    def __init__(self,client,collection,uid,create=True,**kwargs):
        self.collection = collection
        self.model = entity(uid=uid, collection=collection,**kwargs)
        super(Entity, self).__init__(client,**kwargs)
        if create:
            self.this = self.update_or_create(client)
        

    def collection(self,client):
        '''collection will return the collection associated with
        the entity
        '''
        return client.get(collection.key)


    def images(self,client):
        '''images will return images associated with the entity
        '''
        key = self.get_keypath()
        return client.get(client.key(*key, "Images"))
    

    def text(self,client):
        '''text will return text associated with the entity
        '''
        key = self.get_keypath()
        return client.get(client.key(*key, "Text"))


class Image(ModelBase):

    def __init__(self,client,uid,entity,download,url,storage,
                 description=None,metadata=None,create=True,**kwargs):
        self.entity = entity
        self.model = image(uid=uid,
                           entity=entity,
                           download=download,
                           url=url,
                           description=description,
                           storage=storage,
                           metadata=metadata)
        super(Image, self).__init__(**kwargs)
        if create:
            self.this = self.update_or_create(client)

    def __repr__(self):
        return self.this


class Text(ModelBase):

    def __init__(self,client,uid,entity,content,create=True,**kwargs):
        self.entity = entity
        self.model = text(uid=uid,
                          entity=entity,
                          content=content,
                          description=description,
                          metadata=metadata)
        super(Text, self).__init__(**kwargs)
        if create:
            self.this = self.get_or_create(client)

    def __repr__(self):
        return self.this



######################################################################################
# Radiology Client to interact with Models
######################################################################################


class Client(ClientBase):

    def __init__(self,**kwargs):
        self.bucket_name = 'radiology'
        self.batch = BatchManager()
        super(Client, self).__init__(**kwargs)
    
    def __str__(self):
        return "storage.google.%s" %self.bucket_name

    def __repr__(self):
        return "storage.google.%s" %self.bucket_name


    ###################################################################
    ## Create and get #################################################
    ###################################################################

    def get_collection(self,fields):
        return Collection(client=self.datastore,**fields)

    def get_entity(self,fields):
        return Entity(client=self.datastore,**fields)

    def create_image(self,create=True,**fields):
        new_image = Image(client=self.datastore,create=create,**fields)
        # TODO: need to think about how we want to also upload to storage -
        # Add an operation to batch? have a second batch? do them in pairs?
        # need to think abut this

    def create_text(self,fields,create=True,**kwargs):
        # STOPPED HERE - need to make sure args TO this function are ok,
        # and the Text object below takes in the entity, etc.
        new_text = Text(client=self.datastore,**kwargs)

    def get_storage_path(self,file_path,collection_name,return_folder=False):
        folder = file_path.split(collection_name)[1]
        bucket_path = "%s%s" %(collection_name,
                               folder)
        if return_folder:
            return os.path.dirname(bucket_path)
        return bucket_path



    ###################################################################
    ## Upload #########################################################
    ###################################################################


    def upload_texts(self,texts,entity,batch=True):
        '''upload_texts will add text objects to the batch manager'''
        new_texts = []
        for txt in texts:
            uid = self.get_storage_path(txt['original'],collection_name)
            with open(txt['original'],'r') as filey:
                content = filey.read()
            new_text = self.create_text(uid=uid,
                                        content=content,
                                        entity_id=entity.key,
                                        create=not batch) # Create if not doing batch
            if batch:
                self.batch.add(new_text)
            new_texts.append(new_text)
        return new_texts


    def upload_images(self,images,entity,collection_name,batch=True):
        '''upload_images will add image objects to the batch manager, or create
        one at a time
        '''
        new_images = []
        for img in images:
            bucket_folder = self.get_storage_path(img['original'],collection_name)
            image_obj = self.upload_object(file_path=img['original'],
                                           bucket_folder=bucket_folder)

            url = self.get_storage_path(image_obj['name'],collection_name)

            new_image = self.create_image(uid=image_obj['id'],
                                          entity_id=entity.key,
                                          download=image_obj['mediaLink'],
                                          url=url,
                                          storage=image_obj,
                                          create=not batch)
            new_images.append(new_image)
            if batch:
                batch.add(new_image)

        return new_images


    def upload_dataset(self,structures,batch=True):
        '''upload takes a list of structures (eg from som.wordfish.structures
        and uploads to storage and datastore. 
        :param structures: the list of wordfish data structures
        :param batch: add entities in batches (recommended, default True)
        '''
        
        if not isinstance(structures,list):
            structures = [structures]

        # Each structure corresponds to a collection, a subset of entities
        for coll in structures:

            # The structure should be created first
            uid = os.path.basename(coll['collection']['name'])
            fields = {'uid': uid }
            if 'metadata' in coll['collection']:
                fields['metadata'] = read_json(coll['collection']['metadata'])        
            new_collection = self.get_collection(fields)

            # Add entities
            if 'entities' in coll['collection']:
                for ntt in coll['collection']['entities']:
                    
                    fields = {'uid': os.path.basename(ntt['entity']['id']),
                              'collection':col }
                    entity = self.get_entity(fields)
                   
                    # Add images and text to entities
                    if 'texts' in ntt['entity']:
                        new_texts = self.upload_texts(texts=ntt['entity']['texts'],
                                                      entity=entity,
                                                      batch=batch)

                    if 'images' in ntt['entity']:
                        new_images = self.upload_images(images=ntt['entity']['images'],
                                                        entity=entity,
                                                        batch=batch)

                    # Run a transaction for put (insert) images and text, and clears queue
                    self.batch.insert()
