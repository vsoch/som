#!/usr/bin/env python

'''
utils.py: general http functions (utils) for som api

'''

from som.logman import bot
from som.api.base import (
    api_base,
    api_version
)

import requests
import os
import sys

#TODO: add retrying, ask Susan/Garrick about number of times
# (I think we should do exponential retry)


def api_get(url,headers=None,token=None,data=None, return_json=True):
    '''api_get will use requests to get a particular url
    :param url: the url to send file to
    :param headers: a dictionary with headers for the request
    :param putdata: additional data to add to the request
    :param return_json: return json if successful
    '''
    bot.logger.debug("GET %s",url)

    if headers == None:
        headers = get_headers(token=token)
    if data == None:
        response = requests.get(url,         
                                headers=headers)
    else:
        response = requests.get(url,         
                                headers=headers,
                                json=data)

    if response.status_code == 200 and return_json:
        return response.json()

    return response


def api_put(url,headers=None,token=None,data=None, return_json=True):
    '''api_put will send a read file (spec) to Singularity Hub with a particular set of headers
    :param url: the url to send file to
    :param headers: the headers to get
    :param headers: a dictionary with headers for the request
    :param data: additional data to add to the request
    :param return_json: return json if successful
    '''
    bot.logger.debug("PUT %s",url)

    if headers == None:
        headers = get_headers(token=token)
    if data == None:
        response = requests.put(url,         
                                headers=headers)
    else:
        response = requests.put(url,         
                                headers=headers,
                                json=data)
    
    if response.status_code == 200 and return_json:
        return response.json()

    return response


def api_post(url,headers=None,data=None,token=None,return_json=True):
    '''api_get will use requests to get a particular url
    :param url: the url to send file to
    :param headers: a dictionary with headers for the request
    :param data: additional data to add to the request
    :param return_json: return json if successful
    '''
    bot.logger.debug("POST %s",url)

    if headers == None:
        headers = get_headers(token=token)
    if data == None:
        response = requests.post(url,         
                                 headers=headers)
    else:
        response = requests.post(url,         
                                 headers=headers,
                                 json=data)

    if response.status_code == 200 and return_json:
        return response.json()

    return response
