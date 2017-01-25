#!/usr/bin/env python

'''
base.py: base module for working with som api

'''

from som.logman import bot

from som.utils import (
    get_installdir, 
    read_file, 
    write_file
)

from som.api.validators.requests import (
    validate_person,
    validate_items,
    validate_item
)

from som.api.validators.utils import (
    get_universal_source
)

from som.api.standards import (
    api_base,
    api_version
)

import subprocess
import tempfile
import zipfile
import inspect
import shutil
import requests
import imp
import sys
import re
import os


api_base = "https://api.rit.stanford.edu"
api_version = "v1"


def create_identifiers(person,items=None):
    '''create_identifiers will return a json (dict) of identifiers for a request.
    Currently, this function servies to check that a "person" object is included 
    (required) and allows for (optional) items.
    :param person: the person dictionary, which must have the following:
    '''
    identifiers = {"person": person}
    if items != None:
        if not isinstance(items,list):
            items = [items]
        
        identifiers['items'] = items
    return identifiers


def create_person(person_id,id_source,id_timestamp=None,custom_fields=None,sources=None):
    '''create person will return a json (dict) of required elements for a person,
    a field to go under an identifier. The following is required:
    :param person_id: mandatory key for uniquely identifying the person (e.g. "1234567-8")
    :param id_source: mandatory issuer for the above id (e.g., "stanford")
    :param id_timestamp: when the id was looked up, to help with changed/merged ids (optional)
    :param custom_fields: not required, a dictionary of custom key pairs to include as data
    :param sources: a custom list of sources (eg, ['stanford']) to accept. If not defined, defaults
    are used
    :returns person: a person data structure, not wrapped, or None if not valid
    '''
    person = {"id":person_id,
              "id_source":id_source}

    # Custom fields and id_timestamp are optional
    if custom_fields != None:
        person['custom_fields'] = custom_fields 

    if id_timestamp != None:
        person["id_timestamp"] = id_timestamp

    valid = validate_person(person=person,
                            sources=sources)
    if valid == True:
        return person

    return None


def create_items(item_ids,id_sources,sources=None,custom_fields=None,verbose=False):
    '''create items is a wrapper for create items, taking in lists of item_id and id_source.
    if id_source is not a list, it's assumed to be equivalent for all items.
    :param item_ids: should be a list of items.
    :param id_sources: if a list is given, it must be equal in length to item ids. Otherwise,
    the common identifier (one term) is used for all items.
    :param custom_fields: not required, a list of dict of custom key pairs to include as data, or a single
    custom thing to use as data.
    :param sources: a custom list of sources (eg, ['stanford']) to accept. If not defined, defaults
    are used
    :param verbose: verbose is set to False, assuming we have multiple items! This will simply
    not print successful validations - errors are still printed for user.
    '''
    items = []

    # If item_ids is a string, assume one and put into list
    if not isinstance(item_ids,list):
        item_ids = [item_ids]    

    # If id_source is a list, must be equal in length to ids
    universal_source = get_universal_source(source=id_sources,
                                            comparator=item_ids)

    # If custom_fields is a list, must be equal in length to ids
    universal_field = get_universal_source(source=custom_fields,
                                           comparator=item_ids)

    # Iterate through items to return list of dict
    for i in range(len(item_ids)):

        # Do we have a shared item source?
        if universal_source != None:
            item_source = universal_source
        else:
            item_source = id_sources[i]

        # Do we have a shared custom_fields?
        if universal_field != None:
            item_field = universal_field
        else:
            item_field = custom_fields[i]

        item = create_item(item_id=item_ids[i],
                           id_source=item_source,
                           custom_fields=item_field,
                           sources=sources,
                           verbose=verbose)
    
        items.append({"item":item})
    return items


def create_item(item_id,id_source,custom_fields,sources=None,verbose=True):
    '''create item will take input for an item, and return the item if it's valid
    :param item_id: the item id to store, mandatory
    :param id_source: mandatory issuer for the above id (e.g., "pacs")
    :param custom_fields: not required, a dictionary of custom key pairs to include as data
    :param id_timestamp: when the id was looked up, to help with changed/merged ids (optional)
    :param sources: a custom list of sources (eg, ['stanford']) to accept. If not defined, defaults
    '''
    item = {"id":item_id,
            "id_source":id_source}

    # Custom fields and id_timestamp are optional
    if custom_fields != None:
        item['custom_fields'] = custom_fields 

    if id_timestamp != None:
        item["id_timestamp"] = id_timestamp

    valid = validate_item(item,sources=sources,
                          custom_fields=custom_fields,
                          verbose=verbose)
    if valid == True:
        return item

    return None
