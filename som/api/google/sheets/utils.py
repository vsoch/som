'''
google/utils.py: general storage utility functions

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

from __future__ import print_function
from googleapiclient.errors import HttpError
from googleapiclient import (
    http,
    discovery
)

from oauth2client.client import GoogleCredentials

from som.logger import bot

import httplib2
import os
import re

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage



#######################################################################
# GOOGLE GENERAL API ##################################################
#######################################################################

def get_google_service(service_type=None,version=None):
    '''
    get_google service will use the requests library to get a url
    :param service_type: the service to get (default is storage)
    :param version: version to use (default is v1)
    '''
    if service_type == None:
        service_type = "sheets"
    if version == None:
        version = "v4"

    secrets=os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    if secrets is not None:
        return get_authenticated_service(secrets, service_type, version)

    credentials = GoogleCredentials.get_application_default()
    return discovery.build(service_type, version, credentials=credentials) 


def get_authenticated_service(client_secrets, service_type, version):
    '''use client secrets to get an authenticated credential'''
    credentials = get_credentials(client_secrets)
    http = credentials.authorize(httplib2.Http())

    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=%s' %version)
    return discovery.build(service_type, 
                           version, http=http,
                           discoveryServiceUrl=discoveryUrl)
 


def get_credentials(client_secrets,scope='', flags=None):
    ''' get credentials relies on OAuth2 flow to get and/or update a
    credential. This is based on the Google Python Sheets Quickstart.
    Thanks Google!
    '''
    if scope is not '':
        scope =".%s" %scope

    home = os.path.expanduser('~')
    storage = os.path.join(home, '.credentials')

    if not os.path.exists(storage):
        os.makedirs(storage)

    credential_file  = 'sheets.googleapis.com-python-sendit.json'
    scopes = 'https://www.googleapis.com/auth/spreadsheets%s' %scope
    credential_path = os.path.join(storage, credential_file)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets, scopes)
        flow.user_agent = "Google Sheets Sendit Logger"
        print('Storing credentials to ' + credential_path)
        credentials = tools.run_flow(flow, store, flags)
    return credentials
