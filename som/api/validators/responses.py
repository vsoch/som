#!/usr/bin/env python

'''
validators/responses.py: validation of json responses from api

'''

from som.logman import bot
import os
import sys

from validator import (
    Required, 
    Not, 
    Truthy, 
    Blank, 
    Range, 
    Equals, 
    In, 
    validate
)


def receive_identifiers(response):
    '''receive identifiers will validate reception of an identifiers response
    :param response: the response object

    :: notes
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
    '''
    bot.logger.debug("NOT YET WRITTEN")
    return True
