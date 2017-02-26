#!/usr/bin/env python

'''
base.py: base module for working with som api

'''

from som.logman import bot
from som.api.auth import (
    authenticate,
    get_headers
)

from som.api.utils import (
    api_get,
    api_post,
    api_put
)

from som.api.base import (
    api_base,
    api_version
)

from som.api.client import ClientBase


class Client(ClientBase):

    def __init__(self,**kwargs):
        self.base = self._get_radiology_base()
        super(Client, self).__init__(**kwargs)
    

    def _get_radiology_base(self,base=None,version=None):
        '''get_radiology_base returns the base api for radiology
        :param base: if base URL. If not defined, will use default
        :param version: the api version, in format vX. If not defined,
        will return default
        '''
        if base == None:
            base = api_base
        if version == None:
            version = api_version

        return "%s/%s/uid/radiology" %(base,version)


    def deidentify(self,identifiers):
        '''deidentify will send a post to deidentify one or more images
        POST https://APIBASE/VERSION/radiologydeid    
        :param identifiers: a list of identifiers (people and items)
        '''    
        url = "%sdeid" %(self.base)
        response = api_post(url,headers=self.headers,data=identifiers)
        if "results" in response:
            return response['results']
        return response
