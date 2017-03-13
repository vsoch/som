#!/usr/bin/env python

'''
base.py: base module for working with som api

'''

from som.logman import bot

from som.api.utils import (
    api_get,
    api_post,
    api_put
)

from som.api.client import ClientBase


class Client(ClientBase):

    def __init__(self,**kwargs):
        super(Client, self).__init__(**kwargs)
        self.study = 'radiologydeid'
   
    def deidentify(self,identifiers):
        '''deidentify will send a post to deidentify one or more images
        POST https://APIBASE/VERSION/radiologydeid    
        :param identifiers: a list of identifiers (people and items)
        '''    
        url = "%sdeid" %(self.studybase)
        response = api_post(url,headers=self.headers,data=identifiers)
        if "results" in response:
            return response['results']
        return response
