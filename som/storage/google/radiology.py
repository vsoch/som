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


