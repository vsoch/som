#!/usr/bin/env python

'''
validators/responses.py: validation of json responses from api

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


'''

from som.logger import bot
import os
import sys

from validator import (
    Required, 
    Pattern,
    Not, 
    Truthy, 
    Blank, 
    Range, 
    Equals, 
    In, 
    validate
)

from som.api.identifiers.standards import (
    identifier_sources,
    item_sources,
    timestamp
)

from .utils import validate_fields


def receive_identifiers(response):
    '''receive identifiers will validate reception of an identifiers response.
    This should be a list
    :param response: the response list of identifiers

    :: notes
     successful response:

     HTTP 200

    [
       {'jittered_timestamp': '2016-01-30T17:15:23.123Z', 
        'id': '12345678', 
        'suid': '103e', 
        'id_source': 'Stanford MRN', 
        'custom_fields': [
             {'key': 'studySiteID', 'value': '78329'}], 
        'items': [
                   {
                    'id_source': 'GE PACS', 
                    'jittered_timestamp': '2016-01-15T17:15:23.123Z', 
                    'id': 'A654321', 
                    'suid': '103e'}
                   ]}

    ]

    '''
    # These fields are expected, but not required. We will error
    # if any fields are present outside this scope
    expected_fields = ['items',
                       'id_source', 
                       'jittered_timestamp', 
                       'suid', 
                       'id', 
                       'custom_fields']

    if not isinstance(response,list):
        bot.error("Response must be a list")
        return False

    # These are the rules for each uidEntity
    rules = {
        "id": [Required, Pattern("^[A-Za-z0-9_-]*$")], # pattern
        "suid": [Required, Pattern("^[A-Za-z0-9_-]*$")], # the suid
        "id_source": [Required, In(identifier_sources)],   # must be in identifer sources
        "jittered_timestamp": [Required,Pattern(timestamp)]
    }

    for item in response:

        # Validate required fields
        valid,message = validate(rules, item)
        if valid == False:
            bot.error(message)
            return valid

        # Validate fields returned in response
        if not validate_fields(expected_fields,item.keys()):
            return False

        # Validate items
        if "items" in item:
            if not receive_items(item['items']):
                return False
            
    bot.debug("Identifiers data structure valid: %s" %valid)
    return valid


def receive_items(items):
    '''receive items will validate reception of an items list.
    :param items: the items list from a response

     HTTP 200

        'items': [
                   {
                    'id_source': 'GE PACS', 
                    'jittered_timestamp': '2016-01-15T17:15:23.123Z', 
                    'id': 'A654321', 
                    'suid': '103e'
                    }
         ]

    '''
    expected_fields = ['id_source', 
                       'jittered_timestamp', 
                       'suid', 
                       'id',
                       'custom_fields']

    if not isinstance(items,list):
        bot.error("Items must be a list")
        return False

    # These are the rules for each uidEntity
    rules = {
        "id": [Required, Pattern("^[A-Za-z0-9_-]*$")], # pattern
        "suid": [Required, Pattern("^[A-Za-z0-9_-]*$")], # the suid
        "id_source": [Required, In(item_sources)],   # must be in person sources
        "jittered_timestamp": [Required,Pattern(timestamp)]
    }

    for item in items:

        # Validate required fields
        valid,message = validate(rules, item)
        if valid == False:
            bot.error(message)
            return valid

        # Validate fields returned in response
        if not validate_fields(expected_fields,item.keys()):
            return False

    return valid
