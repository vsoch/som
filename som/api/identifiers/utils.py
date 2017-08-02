'''
utils.py: util functions for returning identifier objects

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

from .validators import (
    get_universal_source,
    validate_identifiers,
    validate_items,
    validate_item
)

import sys
import re
import os


def create_lookup(response,lookup_field=None):
    '''create_identifier_lookup will take a response, which should be a list
    of results (the API returns a "results" object, and the client 
    returns the list under "results". A lookup dictionary is returned,
    indexed by "id"
    '''
    if lookup_field is None:
        lookup_field = "id"

    if not isinstance(response,list):
        response = [response]

    lookup = dict()
    for entry in response:
        key = entry[lookup_field]
        if key in lookup:
            bot.warning("%s already in lookup, will use last in list." %(key))
        lookup[key] = entry
    return lookup
