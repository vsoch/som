#!/usr/bin/env python

'''
validators/requests.py: validation of json (dict) structures to send

'''

from som.logman import bot
from som.api.standards import (
    identifier_sources,
    item_sources,
    timestamp
)

from som.api.validators.utils import validate_fields

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


def validate_identifiers(identifiers,id_sources=None,item_sources=None,verbose=True):
    '''validate_identifiers will validate one or more identifier objects, 
    intended to go in as a field to a POST
    :param identifiers: the identifiers object.
    :param verbose: verbose output for items
    :param identifier_sources: a list of one or more identifier sources. 
    :param item_sources: a list of one or more item sources
    If either not defined, default to use standards

    :: notes
       {
        # mandatory key for uniquely identifying the person
        "id":"1234567-8",
       
        # the issuer for the above id
        # mandatory, or maybe optional with default of "stanford" or "unspecified"
        
        "id_source":"stanford",
        # when the id was looked up, to help with changed/merged ids
        # optional with default of current timestamp?
        
        "id_timestamp":"2016-01-30T17:15:23.123Z",
        # optional key/value attributes, will be stored as-is if provided, but not used or interpreted
        # values will be updated/replaced if sent multiple times (last received wins)
        # any existing values will be preserved if not explicitly set here; set empty string to remove
        
        "custom_fields":{
          "first_name":"Joe",
          "last_name":"Smith",
          "dob":"1970-02-28"
        }
    '''
    if id_sources == None:
        id_sources = identifier_sources

    # These are the rules for a person
    rules = {
        "id": [Required, Pattern("^[A-Za-z0-9_-]*$")], # pattern
        "id_source": [Required, In(id_sources)],   # must be in person sources
        "id_timestamp": [Required,Pattern(timestamp)], 
    }

    if not isinstance(identifiers,dict):
        bot.logger.error("Identifiers data structure must be dictionary.")
        return False

    if "identifiers" not in identifiers:
        bot.logger.error("identifiers key not found in data structure.")

    items = identifiers['identifiers']

    if not isinstance(items,list):
        bot.logger.error("Items in identifiers data structure must be list.")
        return False  

    for item in items:

        valid,message = validate(rules, item)
        if valid == False:
            bot.logger.error(message)
            return valid

        if "items" in item:
            validate_items(item['items'],sources=item_sources)


    bot.logger.debug("Identifiers data structure valid: %s",valid)
    return valid


def validate_items(items,sources=None,verbose=True):
    '''validate_items is a wrapper for "validate_item" to allow for one or more items
    to go through validation at once.
    :param items: one or more items to parse through, a dict or list of dicts
    :param item_sources: custom list of item sources. If not provided, defaults used.
    :param verbose: if True, will output each item that is valid
    '''
    if not isinstance(items,list):
        items = [items]

    for item in items:
        valid = validate_item(item=item,
                              sources=sources,
                              verbose=verbose)
 
        # We stop mid point if we find an invalid item
        if valid == False:
            return valid
 
    # Otherwise, we return all items valid
    return valid


def validate_item(item,sources=None,verbose=True):
    '''validate_item will validate a single item objects, intended to go in as a field to
    a POST. For more than one item, use validate_items wrapper
    :param item: the item object. Must include the following:
    :param sources: a list of valid item sources (eg ["pacs"])
    :param verbose: if True, prints out valid True messages. False (errors) always printed

    :: notes

    {
        # generic attribute/values just to store, not interpreted
        "id":"123123123123123", // mandatory

        # the issuer for the above id
        # mandatory, or maybe optional with default of "stanford" or "unspecified"
        "id_source":"pacs",

        # when the id was looked up, to help with changed/merged ids
        # optional with default of current timestamp?
        "id_timestamp":"2016-01-30T17:15:23.123Z",

        # optional key/value attributes, will be stored as-is if provided, but not used or interpreted
        # values will be updated/replaced if sent multiple times (last received wins)
        # any existing values will be preserved if not explicitly set here; set empty string to remove
        "custom_fields":{
          "image_type":"x-ray",
          "resolution":"high"
    }
    '''
    if sources == None:
        sources = item_sources

    # These are the rules for an item
    rules = {
        "id": [Required, Pattern("^[A-Za-z0-9_-]*$")], # pattern
        "id_source": [Required, In(sources)],      # must be in item sources
        "id_timestamp": [Required,Pattern(timestamp)], 
    }

    valid,message = validate(rules, item)
    if verbose == True:
        bot.logger.debug("identifier %s data structure valid: %s",item['id'],valid)
    if valid == False:
        bot.logger.error(message)
        if verbose == True:
            print(item)
    return valid
