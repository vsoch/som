#!/usr/bin/env python

'''
utils.py: general http functions (utils) for som api

'''

from som.logman import bot
from som.api.base import (
    api_base,
    api_version
)

from som.api.auth import (
    authenticate,
    refresh_access_token
)

import requests
import os
import sys


def api_call(url,func,headers=None,token=None,data=None,return_json=True):
    '''api_call is a template that will take a post, put, or get function
    and insert the right variables.
    :param url: the url to send file to
    :param headers: a dictionary with headers for the request
    :param data: additional data to add to the request
    :param return_json: return json if successful
    '''
    if token == None:
        token = authenticate()

    if headers == None:
        headers = get_headers(token=token)
    response = func(url,headers,json=data)

    # Errored response, try again with refresh
    if response.status_code == 401:
        bot.logger.warning("Expired token, refreshing...")
        token = refresh_access_token()
        response = func(url,headers,json=data)

    if response.status_code == 200 and return_json:
        return response.json()

    return response



def api_put(url,headers=None,token=None,data=None, return_json=True):
    '''api_put will send a read file (spec) to Singularity Hub with a particular set of headers
    '''
    bot.logger.debug("PUT %s",url)
    return api_call(url,
                    func=requests.put,
                    headers=headers,
                    token=token,
                    data=data,
                    return_json=return_json)



def api_post(url,headers=None,data=None,return_json=True,token=None):
    '''api_get will use requests to get a particular url
    '''
    bot.logger.debug("POST %s",url)
    return api_call(url,
                    func=requests.post,
                    headers=headers,
                    token=token,
                    data=data,
                    return_json=return_json)



def api_get(url,headers=None,token=None,data=None, return_json=True):
    '''api_get will use requests to get a particular url
    '''
    bot.logger.debug("GET %s",url)
    return api_call(url,
                    func=requests.get,
                    headers=headers,
                    token=token,
                    data=data,
                    return_json=return_json)
