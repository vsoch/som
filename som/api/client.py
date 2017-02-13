#!/usr/bin/env python

'''
client.py: simple clients for som api

'''

from som.api.auth import (
    authenticate,
    get_headers
)

from som.logman import bot
from som.api.standards import spec



class ClientBase(object):


    def __init__(self, spec=None, token=None):
 
        if spec != None:
            self.spec = spec

        if token == None:
            token = authenticate()

        self.token = token
        self.headers = get_headers(token=token)


    def update_headers(self, headers):
        '''update_headers will add headers to the client
        :param headers: should be a dictionary of key,value to update/add to header
        '''
        for key,value in headers.items():
            self.client.headers[key] = item
