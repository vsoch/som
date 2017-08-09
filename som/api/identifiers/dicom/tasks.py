'''
tasks.py: functions to extract identifiers from dicom images

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
from som.utils import (
    get_listfirst,
    read_json
)

import dateutil.parser
import tempfile

from deid.identifiers import (
    get_timestamp
)

from pydicom.sequence import Sequence

from som.api.identifiers.dicom.settings import (
   entity as entity_options,
   item as item_options
)

import os
import sys


######################################################################
# MAIN GET FUNCTIONS
######################################################################

def prepare_identifiers_request(ids, force=True):
    '''prepare identifiers request takes in the output from deid 
    get_identifiers, and returns the minimal request to send to DASHER.
    The assumption is that one batch of ids ==> one entity / Accession Number
    '''
    
    # Enforce application default
    entity_source = entity_options['id_source']['name']
    entity_field = entity_options['id_source']['field']
    item_source = item_options['id_source']['name']            
    item_field = item_options['id_source']['field']  
    entity_times = entity_options['id_timestamp']
    item_times = item_options['id_timestamp']

    # Entity --> Patient
    entity = {"id_source":entity_source,
              "items":[]}

    # Item --> Study (to represent all images)
    new_item = {"id_source": item_source}
    for item_id,item in ids.items():

        # Entity ID
        if "id" not in entity:
            entity_id = item[entity_field].replace('-','')
            entity["id"] = entity_id

        # Entity timestamp
        if "id_timestamp" not in entity:
            entity_ts = get_listfirst(item=item,group=entity_times['date']) # 20021202
            if entity_ts is not None: 
                timestamp = get_timestamp(item_date=entity_ts)              # 2002-12-02T00:00:00Z
                entity['id_timestamp'] = timestamp

        # Study Timestamp
        if "id_timestamp" not in new_item:
            item_ts = get_listfirst(item=item,group=item_times['date']) 
            if item_ts is not None:
                timestamp = get_timestamp(item_date=item_ts)
                new_item["id_timestamp"] = timestamp

        # Study ID (accession#)
        if "id" not in new_item:
            new_item["id"] = item[item_field]                                        

    # We are only including one study item to represent all images
    entity["items"].append(new_item)

    # Expected format of dasher
    ids = {"identifiers": [entity]}    
    return ids




def prepare_identifiers(response,ids,force=True):
    '''prepare identifiers is the step before replacing identifiers,
    it expects a response from the DASHER API, and will use it to prepare
    custom variables to each item provided in ids. It is assumed that the
    response given is relevant for all items in ids
    : param extracted: a dictionary with key (item id) and value a dictionary
    of extracted fields 
    '''

    # Format data correctly for deid
    for entity in response:      
        item = entity['items'][0]  
        updates = {'item_timestamp': item['jittered_timestamp'],
                   'entity_timestamp': entity['jittered_timestamp'],
                   'entity_id': entity['suid'],
                   'entity_id_source': entity['id_source'],
                   'item_id': item['suid'],
                   'item_id_source': item['id_source'],
                   'jitter': item['jitter'] }

    updated = dict()
    for item_id in ids:
        updated[item_id] = dict()
        updated[item_id].update(ids[item_id])
        for key,value in updates.items():
            updated[item_id][key] = value
    return updated
