'''
tasks.py: general tasks across image types

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
from som.api.identifiers.dicom.settings import (
    entity as entity_options,
    item as item_options
)

import sys
import re
import os


def update_identifiers(ids,updates):
    '''update identifiers expects two dictionaries with the same format:   

    ids['111111']['2.2.222.2222']
       {'key1': 'value1', 'key2': 'value2', .... 'keyN': 'valueN'} 

    and will update fields in ids with matching fields in updates.
    New fields can be added, however the constaint is that the entity
    and items must be present in the original (no new allowed)
    '''
    updated = dict()
    for entity,items in ids.items():
        updated[entity] = dict()
        # First add items already there        
        for item,fields in items.items():
            updated[entity][item] = dict()
            for key,val in fields.items():
                updated[entity][item][key] = val
        # Now update with updates items
        if entity in updates:
            for item, fields in updates[entity].items(): 
                for key,val in fields.items():   
                    updated[entity][item][key] = val  
    return updated
