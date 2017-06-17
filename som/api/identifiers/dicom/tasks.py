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

from deid.dicom import (
    get_files,
    get_identifiers as get,
    replace_identifiers as put,
)

from .settings import (
   entity as entity_options,
   item as item_options
)

import os
import sys
here = os.path.dirname(os.path.abspath(__file__))


######################################################################
# MAIN GET FUNCTIONS
######################################################################

def get_identifiers(dicom_files,force=True):
    '''extract and validate identifiers from a dicom image This function 
    uses the deid standard get_identifiers, and formats the data into 
    what is expected for the SOM API request. 
    :param dicom_files: the dicom file(s) to extract from
    :param force: force reading the file (default True)
    '''
    # Enforce application default
    entity_id = entity_options['id_source']
    item_id = item_options['id_source']

    # get_identifiers: returns ids[entity][item] = {"field":"value"}
    ids = get(dicom_files=dicom_files,
              force=force,
              entity_id=entity_id,
              item_id=item_id)


    bot.verbose("Starting preparation of %s entity for SOM API" %(len(ids)))
    entity_cf = entity_options['custom_fields']
    item_cf = item_options["custom_fields"]
    entity_date = entity_options["PatientBirthDate"]
    entity_times = entity_options['id_timestamp']
    item_times = item_options['id_timestamp']
    

    # Now we build a request from the ids
    request = dict()
    for eid,items in ids.items():
        request[eid] = {"id_source":entity_id,
                        "id":eid,
                        "items":[],
                        "custom_fields":{}}

        bot.debug('entity id: %s' %(eid))
        for iid,item in items.items():
            bot.debug('item id: %s' %(iid))

            # Here we generate a timestamp for the entity
            if "id_timestamp" not in request[eid]:
                entity_ts = get_timestamp(item_date=entity_times['date'])
                request[eid]['id_timestamp'] = entity_ts

            # Generate the timestamp for the item
            item_ts = get_timestamp(item_date=item_times['date'],
                                    item_time=item_times['time'])

            new_item = {"id_source": item_id,
                        "id": iid,
                        "custom_fields":{}}

            for header,value in item.items():
            
                # Is it wanted for the entity?
                if header in entity_cf:
                    request[eid]['custom_fields'][header] = value

                # Is it wanted for the item?
                elif header in item_cf:
                    new_item["custom_fields"][header] = value

            request[eid]["items"].append(new_item)
       
    
    # Upwrap the dictionary to return an identifiers objects with a list of all entities
    ids = {"identifiers": [entity for key,entity in request.items()]}
    return ids




def replace_identifiers(response,dicom_files,force=True,deid=None,
                        output_folder=None,overwrite=True):
    '''replace identifiers will replace dicom_files with a response
    from the identifiers API. 
    :param response: the response from the API, or a list of identifiers
    :param dicom_files: the dicom file(s) to extract from
    :param force: force reading the file (default True)
    :param deid: The deid (recipe for replacement) defaults to SOM deid
    :param output_folder: if not defined, uses temp. directory
    :param overwrite: if False, save updated files to temporary directory

    :: note a response looks like this

    [{'id': '14953772',
      'id_source': 'Stanford MRN',
      'items': [{'custom_fields': [{'key': 'ordValue', 'value': '33.1'}],
        'id': 'MCH',
        'id_source': 'Lab Result',
        'jitter': -19,
        'jittered_timestamp': '2010-01-16T11:50:00-0800',
        'suid': '10f6'}],
      'jitter': -19,
      'jittered_timestamp': '1961-07-08T00:00:00-0700',
      'suid': '10f5'}]
    '''

    # Generate ids dictionary for data put (replace_identifiers) function
    ids = dict()

    # Enforce application default
    entity_id = entity_options['id_source']
    item_id = item_options['id_source']

    if deid is None:
        deid = "%s/deid.som" %(here)

    if not os.path.exists(deid):
        bot.warning("Cannot find deid %s, using defaults." %(deid))


    # Format data correctly for deid
    ids = dict()

    for entity in response:

        eid = entity['id']
        bot.debug('entity id: %s' %(eid))
        ids[eid] = dict()

        for item in result['items']:
            iid = item['id']
            bot.debug('item id: %s' %(iid))

            # Custom variables
            ids[eid][iid] = {'item_timestamp': item['jittered_timestamp'],
                             'entity_timestamp': entity['jittered_timestamp'],
                             'entity_id': entity['suid'],
                             'item_id': item['suid'] }


            # All custom fields (likely not used)
            for field in item['custom_fields']:
                ids[eid][iid][field['key']] = field['value'] 

           
    # Do the request to update the files, get them
    updated_files = put(dicom_files,
                        ids=ids,
                        deid=deid,
                        overwrite=overwrite,
                        output_folder=output_folder,
                        entity_id=entity_id,
                        item_id=item_id,
                        force=force)
                        
    return updated_files
