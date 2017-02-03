#!/usr/bin/env python

'''
base.py: base module for working with som api

'''

from som.logman import bot
from som.auth import (
    authenticate,
    get_headers
)

from som.api.utils import (
    api_get,
    api_post,
    api_put
)

from som.api.base import (
    api_base,
    api_version,
    create_identifiers
)

from som.api.validators.requests import validate_person

def get_radiology_base(base=None,version=None):
    '''get_radiology_base returns the base api for radiology
    :param base: if base URL. If not defined, will use default
    :param version: the api version, in format vX. If not defined,
    will return default
    '''
    if base == None:
        base = api_base
    if version == None:
        version = api_version

    return "%s/radiology/api/%s" %(base,version)


def deidentify(item_id,item_id_source,item_id_timestamp,
               person=None,person_id=None,person_id_source=None,person_id_timestamp=None,
               person_sources=None,person_custom_fields=None,
               item_custom_fields=None,item_sources=None,               
               base=None,version=None,headers=None,verbose=False):
    '''deidentify will send a post to deidentify one or more images
    POST https://APIBASE/radiology/api/APIVERSION/deidentify    

    PERSON
    :param person_id: mandatory key for uniquely identifying the person (e.g. "1234567-8")
    :param person_id_source: mandatory issuer for the above id (e.g., "stanford")
    :param person_id_timestamp: when the id was looked up, to help with changed/merged ids (optional)
    :param person_custom_fields: not required, a dictionary of custom key pairs to include as data
    :param person: if provided, the other fields are not required

    ITEMS
    :param item_id: mandatory key for uniquely identifying the person (e.g. "1234567-8")
    :param item_id_source: mandatory issuer for the above id (e.g., "stanford")
    :param item_id_timestamp: when the id was looked up, to help with changed/merged ids (optional)
    :param item_custom_fields: not required, a list or dictionar of custom key pairs to include as data

    OPTIONAL
    :param person_sources: a custom list of sources (eg, ['stanford']) to accept. If not defined, defaults
    :param base: if base URL. If not defined, will use default
    :param version: the api version, in format vX. If not defined,
    :param headers: a dictionary with headers for the request
    :param verbose: True will print successful items as well (default is False)

    ::notes: default behavior is to exit if the person returns as None, indicating not valid
             error messages (reasons for not valid) are printed by validation functions.

             the same default is used for items. We don't want one item going through and missing
             another (invalid) and then needing to try again.
    '''

    headers = get_headers(token=token)  #TODO: customize this depending
                                        # on whether token required, how passed, etc.

    # Prepare response urls
    base = get_radiology_base(base,version)
    url = "%s/deidentify" %(base)
    bot.logger.debug("POST %s",url)

    # Prepare data
    if person == None:
        person = create_person(person_id=person_id,
                               id_source=person_id_source,
                               id_timestamp=person_id_timestamp,
                               custom_fields=person_custom_fields,
                               sources=person_sources) #verbose True
    else:
        if validate_person(person,sources=person_id_source) == False:
            person = None

    if person == None:
        bot.logger.error("Person not successfully created. Exiting.")
        sys.exit(1)

    # This function requires items, if not needed, should just create person
    items = create_items(item_ids=item_ids,
                         id_sources=item_id_sources,
                         sources=item_sources,
                         custom_fields=item_custom_fields,
                         verbose=verbose)

    identifiers = create_identifiers(person=person,items=items)
    data = {"identifiers":identifiers }

    return api_post(url,headers=headers,data=data)
