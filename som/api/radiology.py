#!/usr/bin/env python

'''
base.py: base module for working with som api

'''

from som.logman import bot
from som.auth import (
    authenticate
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
    get_identifiers
)

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


def deidentify(person_id,person_id_source,person_id_timestamp,person_sources=None,person_custom_fields=None,
               item_id,item_id_source,item_id_timestamp,item_custom_fields=None,item_sources=None,               
               base=None,version=None,headers=None,verbose=False):
    '''deidentify will send a post to deidentify one or more images
    POST https://APIBASE/radiology/api/APIVERSION/deidentify    

    PERSON
    :param person_id: mandatory key for uniquely identifying the person (e.g. "1234567-8")
    :param person_id_source: mandatory issuer for the above id (e.g., "stanford")
    :param person_id_timestamp: when the id was looked up, to help with changed/merged ids (optional)
    :param person_custom_fields: not required, a dictionary of custom key pairs to include as data

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
    person = create_person(person_id=person_id,
                           id_source=person_id_source,
                           id_timestamp=person_id_timestamp,
                           custom_fields=person_custom_fields,
                           sources=person_sources) #verbose True

    if person == None:
        bot.logger.error("Person not successfully created. Exiting.")
        sys.exit(1)

    # This function requires items, if not needed, should just create person
    items = create_items(item_ids=item_ids,
                         id_sources=item_id_sources,
                         sources=item_sources,
                         custom_fields=item_custom_fields,
                         verbose=verbose)

    data = create_identifiers(person=person,items=items)
    return api_post(url,headers=headers,data=data)







Header for authentication: TODO
{
  "identifiers": [
    {
      // must provide person, item, or both
      "person":{
        // mandatory key for uniquely identifying the person
        "id":"1234567-8",
        // the issuer for the above id
        // mandatory, or maybe optional with default of "stanford" or "unspecified"
        "id_source":"stanford",
        // when the id was looked up, to help with changed/merged ids
        // optional with default of current timestamp?
        "id_timestamp":"2016-01-30T17:15:23.123Z",
        // optional key/value attributes, will be stored as-is if provided, but not used or interpreted
        // values will be updated/replaced if sent multiple times (last received wins)
        // any existing values will be preserved if not explicitly set here; set empty string to remove
        "custom_fields":{
          "first_name":"Joe",
          "last_name":"Smith",
          "dob":"1970-02-28"
        }
      },
      "item":{
         // generic attribute/values just to store, not interpreted
        "id":"123123123123123", // mandatory
        // the issuer for the above id
        // mandatory, or maybe optional with default of "stanford" or "unspecified"
        "id_source":"pacs",
        // when the id was looked up, to help with changed/merged ids
        // optional with default of current timestamp?
        "id_timestamp":"2016-01-30T17:15:23.123Z",
        // optional date (format "yyyy-mm-dd") or timestamp for this item's "business date"
        // if this is provided a "fuzzed" value for it will be returned in the response
        // person must be provided if this is provided (because the fuzzing is an offset for the person)
        "effective_timestamp":"2016-01-30T17:15:23.123Z",
        // optional key/value attributes, will be stored as-is if provided, but not used or interpreted
        // values will be updated/replaced if sent multiple times (last received wins)
        // any existing values will be preserved if not explicitly set here; set empty string to remove
        "custom_fields":{
          "image_type":"x-ray",
          "resolution":"high"
        }
      }
    },
    ...
  ]
}

successful response:

HTTP 200
{
  "identifiers": [
    {
      // present if and only if person was in request
      // same person id+source in --> same id here
      "person_opaque_id":"SP123abc123abc...",
      // present if and only if item was in request
      // same id+source in --> same id here
      "item_opaque_id":"ST234def234def...",
      // present if and only if effective_timestamp was provided
      // precision will match that provided in the request
      // timestamp will be shifted by a random offset for the person so 
      // all items for a given person will have the same offset
      "fuzzed_effective_timestamp":"2016-01-30T17:15:23.123Z"
    },
    ...
  ]
}

Proposed API (Original)

POST https://api.rit.stanford.edu/radiology/api/v1/deidentify
Header for authentication: TODO
{
  "images": [
    {
      // Read from the identified image
      // Omit if not available
      "mrn_source":"stanford",
      "mrn":"1234567-8", // mandatory
      "first_name":"Joe",
      "last_name":"Smith",
      "dob":"1970-02-28",
       // generic attribute/values just to store, not interpreted
      "accession_number":"123123123123123", // mandatory
      "image_date":"2016-01-30T17:15:23.123Z"
    },
    ...
  ]
}

successful response:

HTTP 200
{
  "images": [
    {
      "patient_opaque_id":"123abc123abc...", // same mrn in --> same id here
      "image_opaque_id":"234def234def...",
      "image_date_fuzzed":"2016-01-30" // need time too?
    },
    ...
  ]
} 

errors:

HTTP 500, 400
{
  "message": "Something bad happened"
}

HTTP 401 - Need to authenticate


