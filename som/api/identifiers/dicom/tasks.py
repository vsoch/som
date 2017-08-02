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

def prepare_identifiers_request(ids,
                                force=True,
                                entity_custom_fields=True,
                                item_custom_fields=False):
    '''prepare identifiers request takes in the output from deid 
    get_identifiers, and returns the minimal request to send to DASHER.
    If entity/item_custom_fields is False (recommended for items) 
    no extra data is sent. This is suggested to optimize sending more data faster
    '''

    # Enforce application default
    entity_id = entity_options['id_source']
    item_id = item_options['id_source']            
    entity_cf = entity_options['custom_fields']
    entity_times = entity_options['id_timestamp']
    item_times = item_options['id_timestamp']

    # Now we build a request from the ids
    request = dict()
    for eid,items in ids.items():
        added = []
        request[eid] = {"id_source":entity_id,
                        "id":eid,
                        "items":[],
                        "custom_fields":[]}
        bot.debug('entity id: %s >> %s items' %(eid,len(items)))
        for iid,item in items.items():

            # Here we generate a timestamp for the entity
            if "id_timestamp" not in request[eid]:
                if entity_times['date'] in item:
                    entity_ts = item[entity_times['date']]
                    entity_ts = get_timestamp(item_date=entity_ts)
                    request[eid]['id_timestamp'] = entity_ts

            # Generate the timestamp for the item
            item_ts = None
            for item_date_field in item_times['date']: 
                if item_date_field in item and not item_ts:
                    item_ts = item[item_date_field]

            # We fall back to providing a blank timestamp
            if item_ts is not None:
                item_ts = get_timestamp(item_date=item_ts)
            new_item = {"id_source": item_id,
                        "id_timestamp": item_ts,
                        "id": iid,
                        "custom_fields":[]}

            # Add custom fields, making json serializable
            for header,value in item.items(): 
                parse_customfield = False
                if header in entity_cf and entity_custom_fields is True and header not in added:
                    parse_customfield = True
                    added.append(header) # otherwise would add to entity more than once
                elif item_custom_fields is True:
                    parse_customfield = True
                if parse_customfield is True:

                    # Skip sequence data for now
                    if not isinstance(value,Sequence):
                        if isinstance(value,bytes):
                            value = value.decode('utf-8')
                        cf_entry = {"key": header,
                                    "value": str(value)}

                        # Is it wanted for the entity?
                        if header in entity_cf:
                            request[eid]['custom_fields'].append(cf_entry)

                        # Put everything else in items
                        else:
                            new_item["custom_fields"].append(cf_entry)
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
            for field in item['custom_fields']:
                ids[eid][iid][field['key']] = field['value']
    return ids
