cd b#!/usr/bin/env python

'''
base.py: base module for working with som api

'''

from som.storage.google.client import ClientBase
from som.storage.google.models import *
from som.storage.google.utils import *
from som.logman import bot
from som.utils import read_json
from som.wordfish.structures import structure_dataset


######################################################################################
# Specs and base data structures for each radiology model
######################################################################################


def entity(uid,collection,metadata=None):
    '''entity returns an entity object
    parent is a collection
    '''
    fields = [{'key':'uid','required':True,'value':uid},
              {'key':'metadata','required':False,'value':metadata}]

    model = {'fields':fields,
             'key':['Collection',collection,'Entity', uid]}

    return model



def collection(name,description=None,metadata=None):
    '''entity returns an entity object
    parent is an owner
    '''
    fields = [{'key':'name','required':True,'value':name},
              {'key':'description','required':False,'value':description},
              {'key':'metadata','required':False,'value':metadata}]

    model = {'fields':fields,
             'exclude_from_indexes': ['metadata','description'],
             'key':['Collection', name]}
    return model
    


def image(uid,entity,file_path,description=None,metadata=None):
    '''image returns an image object. entity is the parent
    '''
    fields = [{'key':'name','required':True,'value':uid},
              {'key':'description','required':False,'value':description},
              {'key':'metadata','required':False,'value':metadata},
              {'key':'file_path','required':True,'value':file_path}]

    model = {'fields':fields,
             'key':['Entity',entity,'Image', uid]}
    return model
    


def text(uid,entity,file_path,description=None,metadata=None):
    '''text returns a text object. entity is the parent
    '''
    fields = [{'key':'uid','required':True,'value':uid},
              {'key':'description','required':False,'value':description},
              {'key':'metadata','required':False,'value':metadata},
              {'key':'file_path','required':True,'value':file_path}]

    model =  {'fields':fields,
             'key':['Entity',entity,'Text', uid]}
    return model




######################################################################################
# Core Models, extending base model
######################################################################################


class Collection(ModelBase):
  
    def __init__(self,client,collection_name,**kwargs):
        self.model = collection(name=collection_name,**kwargs)
        self.model['fields'] = validate_model(self.model['fields'])
        super(Collection, self).__init__(client,**kwargs)
        self.this = self.get_or_create(client)


class Entity(ModelBase):

    def __init__(self,client,collection_name,**kwargs):
        self.collection = collection_name
        self.model = entity(uid=uid,
                            collection_name=collection_name,**kwargs)
        self.model['fields'] = validate_model(self.model['fields'])
        self.this = self.get_or_create(client)
        super(Entity, self).__init__(**kwargs)

   
    def collection(self,client):
        '''collection will return the collection associated with
        the entity
        '''
        return client.get(client.key("Collection",self.collection))


    def images(self,client):
        '''images will return images associated with the entity
        '''
        return client.get(client.key(*self.key, "Images"))
    

    def text(self,client):
        '''text will return text associated with the entity
        '''
        return client.get(client.key(*self.key, "Text"))


class Image(ModelBase):

    def __init__(self,client,entity_id,**kwargs):
        self.entity = entity_id
        self.model = image
        self.model['fields'] = validate_model(self.model['fields'])
        self.this = self.get_or_create(client)
        super(Image, self).__init__(**kwargs)

    def __repr__(self):
        return self.this


class Text(ModelBase):

    def __init__(self,client,entity_id,**kwargs):
        self.entity = entity_id
        self.model = text
        self.model['fields'] = validate_model(self.model['fields'])
        self.this = self.get_or_create(client)
        super(Text, self).__init__(**kwargs)

    def __repr__(self):
        return self.this



######################################################################################
# Radiology Client to interact with Models
######################################################################################


class Client(ClientBase):

    def __init__(self,**kwargs):
        self.bucket_name = 'radiology'
        super(Client, self).__init__(**kwargs)
    
    def __str__(self):
        return "storage.google.%s" %self.bucket_name

    def __repr__(self):
        return "storage.google.%s" %self.bucket_name


    def get_collection(self,name):
        return Collection(client=self.datastore,
                          collection_name=name)

    def get_entity(self,**kwargs):
        return Entity(client=self.datastore,**kwargs)

    def get_image(self,**kwargs):
        return Image(client=self.datastore,**kwargs)

    def get_text(self,**kwargs):
        return Text(client=self.datastore,**kwargs)

    def upload(self,structures,dataset_name=None):
        '''upload takes a list of structures (eg from som.wordfish.structures
        and uploads to storage and datastore. 
        '''
        
        if not isinstance(structures,list):
            structures = [structures]
        for s in structures:
            fields = {'name': os.path.basename(s['collection']['name'])}
            if 'metadata' in s['collection']:
                fields['metadata'] = read_json(s['collection']['metadata'])        
            c = self.get_collection(name=fields['name'])

            # Add entities
            if 'entities' in s['collection']:
                for entity in s['collection']['entities']:
                    fields = {'uid': os.path.basename(entity['entity']['id'])}
                    e = self.get_entity(collection=c.key)
                   
                    # Add images and text to entities
                    if 'texts' in entity['entity']:
                        for text in entity['entity']['texts']:
                            #TODO: upload to google cloud storage here, get image URL
                            t = get_text(entity=entity.key)                    

                    if 'images' in entity['entity']:
                        for image in entity['entity']['images']:
                            #TODO: upload to google cloud storage here, get image URL
                            i = get_image(entity=entity.key)                    

            # ahhhh I'm hungry!
