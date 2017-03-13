#!/usr/bin/env python

'''
connect.py: an object to manage a connection to the SOM API

'''

from som.logman import bot

from som.utils import (
    read_file,
    read_json,
    write_json
)

from som.api.auth import (
    authenticate,
    refresh_access_token
)

import json
import os
import requests
import sys


class ApiConnection(object):


    def __init__(self, token=None):
 
        self.headers = None
        if token is None:
            self.token = authenticate()
        else:
            self.token = token
        self.update_headers()
        

    def get_headers(self):
        return self.headers

    def _init_headers(self):
        return {'Content-Type':"application/json"}


    def update_headers(self,fields=None):
        '''get_headers will return a simple default header for a json
        post. This function will be adopted as needed.
        '''
        if self.headers is None:
            headers = self._init_headers()
        else:
            headers = self.headers

        if self.token is not None:
            headers["Authorization"] = "Bearer %s" %(self.token)

        if fields is not None:
            for key,value in fields.items():
                headers[key] = value

        header_names = ",".join(list(headers.keys()))
        bot.logger.debug("Headers found: %s",header_names)
        self.headers = headers


    def put(self,url,data=None,return_json=True):
        '''put will send a read file (spec) to Singularity Hub with a particular set of headers
        '''
        bot.logger.debug("PUT %s",url)
        return self.call(url,
                        func=requests.put,
                        data=data,
                        return_json=return_json)



    def post(self,url,data=None,return_json=True):
        '''post will use requests to get a particular url
        '''
        bot.logger.debug("POST %s",url)
        return self.call(url,
                        func=requests.post,
                        data=data,
                        return_json=return_json)



    def get(self,url,headers=None,token=None,data=None, return_json=True):
        '''get will use requests to get a particular url
        '''
        bot.logger.debug("GET %s",url)
        return self.call(url,
                        func=requests.get,
                        data=data,
                        return_json=return_json)





    def call(self,url,func,data=None,return_json=True):
        '''call is a template that will take a post, put, or get function
        and insert the right variables.
        :param url: the url to send file to
        :param data: additional data to add to the request
        :param return_json: return json if successful
        '''
        response = func(url,self.headers,json=data)

        # Errored response, try again with refresh
        if response.status_code == 401:
            bot.logger.warning("Expired token, refreshing...")
            self.token = refresh_access_token()
            response = func(url,self.headers,json=data)

        if response.status_code == 200 and return_json:
            return response.json()

        return response
