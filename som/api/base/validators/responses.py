#!/usr/bin/env python

'''
validators/responses.py: validation of json responses from api

'''

from som.logman import bot
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

from som.api.standards import (
    identifier_sources,
    item_sources,
    timestamp
)

from som.api.validators.utils import validate_fields


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
        bot.logger.error("Response must be a list")
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
            bot.logger.error(message)
            return valid

        # Validate fields returned in response
        if not validate_fields(expected_fields,item.keys()):
            return False

        # Validate items
        if "items" in item:
            if not receive_items(item['items']):
                return False
            
    bot.logger.debug("Identifiers data structure valid: %s",valid)
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
        bot.logger.error("Items must be a list")
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
            bot.logger.error(message)
            return valid

        # Validate fields returned in response
        if not validate_fields(expected_fields,item.keys()):
            return False

    return valid
