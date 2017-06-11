'''

som.api: base template for making a connection to an API

'''

from som.logger import bot
import requests
import json
import sys
import re
import os


class ApiConnection(object):

    def __init__(self, token=None):
 
        self.headers = None
        if token is not None:
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
        bot.debug("Headers found: %s" %header_names)
        self.headers = headers


    def put(self,url,data=None,return_json=True):
        '''put request
        '''
        bot.debug("PUT %s" %url)
        return self.call(url,
                         func=requests.put,
                         data=data,
                         return_json=return_json)



    def post(self,url,data=None,return_json=True):
        '''post will use requests to get a particular url
        '''
        bot.debug("POST %s" %url)
        return self.call(url,
                        func=requests.post,
                        data=data,
                        return_json=return_json)



    def get(self,url,headers=None,token=None,data=None, return_json=True):
        '''get will use requests to get a particular url
        '''
        bot.debug("GET %s" %url)
        return self.call(url,
                        func=requests.get,
                        data=data,
                        return_json=return_json)



    def call(self,url,func,data=None,return_json=True):
        '''call is a template that will take a post, put, or get function
        and insert the right variables.
        '''
        response = func(url,headers=self.headers,
                            data=json.dumps(data))

        if response.status_code == 200 and return_json:
            return response.json()

        return response
