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


import importlib
from som.logger import bot
from som.utils import (
    read_json
)

from pydicom import read_file
from pydicom.errors import InvalidDicomError
import dateutil.parser

here = os.path.dirname(os.path.abspath(__file__))

def get_func(function_name):
    '''get_func will return a function that is defined from a string.
    the function is assumed to be in this file
    '''
    env = globals()
    if function_name in env:
        return env[function_name]
    return None

######################################################################
# CONFIG DEFINED FUNCS
######################################################################

def get_item_timestamp(dicom):
    '''get_item_timestamp will return the UTC time for an instance.
    This is derived from the InstanceCreationDate and InstanceCreationTime
    If the Time is not set, only the date is used.
    # testing function https://gist.github.com/vsoch/23d6b313bd231cad855877dc544c98ed
    '''
    item_time = dicom.get("InstanceCreationTime","")
    item_date = dicom.get("InstanceCreationDate")
    timestamp = dateutil.parser.parse("%s%s" %(item_date,item_time))
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_entity_timestamp(dicom):
    '''get_entity_timestamp will return a UTC timestamp for the entity,
    derived from the patient's birthdate. In the config.json, this is
    set by setting type=func, and value=get_entity_timestamp
    '''
    item_date = dicom.get("PatientBirthDate")
    timestamp = dateutil.parser.parse("%s" %(item_date))
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")


######################################################################
# MAIN GET FUNCTIONS
######################################################################

def get_identifier(tag,dicom,template):
    '''get_id will use a template and an image to return the user's
    preference for some identifier
    :param tag: the name of the identifier (eg, id, id_source)
    :param dicom: the dicom image, already read in
    :param template: the config['item']/config['entity'] template
    '''
    result = None
    if tag in template:
        action = template[tag]['type']
        value = template[tag]['value']

        # Extracted from data
        if action == "data":
            if isinstance(value,list):
                result = [{"key":x,"value":dicom.get(x)} for x in value if 
                          dicom.get(x,None) is not None]
            else:
                result = dicom.get(value)

        # Custom function in this file that takes dicom image
        elif action == "func":
            func = get_func(value)
            result = func(dicom)

        elif action == "default":
            result = value

        # Retrieve from environment
        elif action == "env":
            if isinstance(value,list):
                result = [os.environ.get(x) for x in value if 
                          os.environ.get(x) is not None]
            else:
                result = os.environ.get(value)
    return result


def get_identifiers(dicom_files,force=True,config=None):
    '''extract and validate identifiers from a dicom image that conform
    to the expected request to the identifiers api.
    :param dicom_files: the dicom file(s) to extract from
    :param force: force reading the file (default True)
    :param config: if None, uses default in provided module folder
    '''

    if config is None:
        config = "%s/config.json" %(here)

    if not os.path.exists(config):
        bot.error("Cannot find config %s, exiting" %(config))

    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]

    ids = dict() # identifiers

    for dicom_file in dicom_files:

        dicom = read_file(dicom_file,force=True)

        # Read in / calculate preferred values
        entity_id = get_identifier(tag='id',
                                   dicom=dicom,
                                   template=config['entity'])

        source_id = get_identifier(tag='id_source',
                                   dicom=dicom,
                                   template=config['entity'])

        item_id = get_identifier('id',
                                 dicom=dicom,
                                 template=config['item'])

        entity_fields = get_identifer('custom_fields',
                                      dicom=dicom,
                                      template=config['entity'])

        item_source = get_identifier('id_source',
                                     dicom=dicom,
                                     template=config['item'])

        item_fields = get_identifer('custom_fields',
                                     dicom=dicom,
                                     template=config['item'])

        # Skip images without patient id or item id
        if entity_id is not None and item_id is not None:

           # Only need to add the entity once
           if entity_id not in ids:
               ids[entity_id] = {'identifiers': { 'id': entity_id } } 
               ids[entity_id]['items'] = []
               ids[entity_id]['identifiers']['custom_fields'] = custom_fields


           # Item is always added
           item = dict()
           item['custom_fields'] = item_fields
           item['id_source'] = item_source
           ids[entity_id]['items'].append(item) 

        else:
            bot.warning("Skipping %s due to empty entity (%s) or item (%s) id" %(dicom_file,entity_id,item_id))
    return ids



def replace_identifiers(response,dicom_files,force=True,config=None):
    '''replace identifiers will replace dicom_files with a response
    from the identifiers API
    :param response: the response from the API
    :param dicom_files: the dicom file(s) to extract from
    :param force: force reading the file (default True)
    :param config: if None, uses default in provided module folder
    '''
    ## FUNCTION NOT FINISHED YET

    if config is None:
        config = "%s/config.json" %(here)

    if not os.path.exists(config):
        bot.error("Cannot find config %s, exiting" %(config))

    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]

    ##TODO: write when I have a working response.

    ## Actions for each come from config
    actions = config['response']['actions']

    # Add fields from 
    additions = config['response']['additions']
    default = actions['*']

    ##TODO: go through fields of data, if in actions, do action
    # if not, go to default. Return list of fixed dicoms.
