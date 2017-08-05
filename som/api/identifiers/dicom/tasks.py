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
    If entity/item_custom_fields is False (recommended for items) 
    no extra data is sent. This is suggested to optimize sending more data faster
    if the entity ID source string needs to be customized from the index value,
    set this in custom_entity_id_source
    '''
    # Enforce application default
    entity_source = entity_options['id_source']['name']
    entity_field = entity_options['id_source']['field']
    item_source = item_options['id_source']['name']            
    item_field = item_options['id_source']['field']  
    entity_times = entity_options['id_timestamp']
    item_times = item_options['id_timestamp']

    request = dict()

    for eid,items in ids.items():

        # Entity --> Patient
        request[eid] = {"id_source":entity_source,
                        "items":[]}

        # Item --> Study (to represent all images)
        new_item = {"id_source": item_source}
        bot.debug('entity id: %s >> %s items' %(eid,len(items)))

        # Build request item until we have all fields        
        for iid,item in items.items():

            # Entity ID
            if "id" not in request[eid]:
                request[eid]["id"] = item[entity_field]

            # Entity timestamp
            if "id_timestamp" not in request[eid]:
                entity_ts = get_listfirst(item=item,group=entity_times['date'])
                if entity_ts is not None:
                    timestamp = get_timestamp(item_date=entity_ts)
                    request[eid]['id_timestamp'] = timestamp

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
        request[eid]["items"].append(new_item)

    # Upwrap the dictionary to return an identifiers objects with a list of all entities
    ids = {"identifiers": [entity for key,entity in request.items()]}    
    return ids




def prepare_identifiers(response,force=True):
    '''prepare identifiers is the step before replacing identifiers,
    taking in a respones from the DASHER API and a list of files, and
    returning an ids data structure for deid. This is useful in the case
    that you need to use or inspect the data structure before using deid.
    '''
    # Generate ids dictionary for data put (replace_identifiers) function
    ids = dict()
    # Enforce application default
    entity_id = entity_options['id_source']
    item_id = item_options['id_source']
    # Format data correctly for deid
    ids = dict()
    for entity in response:
        eid = entity['id']
        bot.debug('entity id: %s' %(eid))
        ids[eid] = dict()
            for item in entity['items']:
                iid = item['id']
            # Custom variables
            ids[eid][iid] = {'item_timestamp': item['jittered_timestamp'],
                             'entity_timestamp': entity['jittered_timestamp'],
                             'entity_id': entity['suid'],
                             'item_id': item['suid'],
                             'jitter': item['jitter'] }
            # All custom fields (likely not used)
            if "custom_fields" in item:
                for field in item['custom_fields']:
                    ids[eid][iid][field['key']] = field['value']
    return ids
