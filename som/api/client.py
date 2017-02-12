#!/usr/bin/env python

'''
client.py: simple clients for som api

'''

from som.api.auth import authenticate
from som.api.standards import spec

from pyswagger.core import BaseClient
from pyswagger import (
    SwaggerApp, 
    SwaggerSecurity
)

from pyswagger.contrib.client.requests import Client as SwaggerClient

def get_client(spec_file=None,token=None):
    '''get_client will return a simple client for a json spec and token
    using pyswagger
    :param spec_file: the spec file to use. If one not provided, the standard is used
    :param token: a token. if none is provided, one is obtained from environment and then
    from home
    ''' 
    if spec_file == None:
        spec_file = spec

    if token == None:
        token = authenticate()

    return Client(spec=spec_file,token=token)


class Client(object):

    def __init__(self, spec=None, token=None):
        self.token = token
        self.app = SwaggerApp._create_(spec)
        self.auth = SwaggerSecurity(self.app)
        self.client = SwaggerClient(self.auth)
        self.client._Client__s.headers['Authorization'] = 'Bearer %s' %(self.token)

    def update_headers(self, headers):
        '''update_headers will add headers to the client
        :param headers: should be a dictionary of key,value to update/add to header
        '''
        for key,value in headers.items():
            self.client._Client__s.headers[key] = item

    def request(self, endpoint, params, headers=None):
        '''request is a wrapper for a pyswagger request
        '''
        if headers != None:
            self.update_headers(headers)
        params['token'] = self.token
        signal = self.app.op[endpoint](**params)
        response = self.client.request(signal)
        return response
