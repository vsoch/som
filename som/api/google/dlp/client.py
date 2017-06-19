'''
api.google.dlp: the base connection to the google DLP API

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

api_base = "https://dlp.googleapis.com"
api_version = "v2beta1"

from som.logger import bot
from som.api import ApiConnection
from som.api.google.dlp.utils import *

import datetime

from oauth2client.client import GoogleCredentials
from apiclient.discovery import build

class DLPApiConnection(ApiConnection):

    def __init__(self,get_service=True,**kwargs):
        self.token = None
        if 'token' in kwargs:
            self.token = token
        super(DLPApiConnection, self).__init__(**kwargs)
        if get_service is True:
            self.get_service()
        
    def get_service(self):
        credentials = GoogleCredentials.get_application_default()
        self.service = build('dlp', api_version, credentials=credentials)

    def inspect(self,texts,include_quote=True,min_level=None):
        '''inspect will inspect a dump of text for identifiers
        :param include_quote: include quotes in the query?
        :param min_level: the minimum likilihood level to return
        '''
        if not isinstance(texts,list):
            texts = [texts]

        if min_level is None:
            min_level = 'LIKELIHOOD_UNSPECIFIED'

        config = {'includeQuote': include_quote,
                  'infoTypes': [],
                  'maxFindings': 0,
                  'minLikelihood': min_level }
        
        items = []
        for text in texts:
            new_item = {'type': 'text/plain',
                        'value': text }
            items.append(new_item)

        groups = paginate_items(items,size=100)
        
        results = []
        for idx in range(len(groups)):
            bot.debug("inspecting for %s of %s" %(idx+1,len(groups)))
            items = groups[idx]
            body = {'inspectConfig': config,
                    'items': items }
            result = self.service.content().inspect(body=body).execute()
            results = results + result['results']
        return results


    def remove_phi(self,texts,include_quote=True,min_level=None):
        '''remove_phi will first use inspect to find PHI, and then
        prepare the equivalent text with the phi removed.
        :param include_quote: include quotes in the query?
        :param min_level: the minimum likilihood level to return
        '''
        if not isinstance(texts,list):
            texts = [texts]

        results =  self.inspect(texts=texts,
                                include_quote=include_quote,
                                min_level=min_level)

        # We will return an equivalent list with phi removed
        cleaned = []

        for idx in range(len(results)):
            result = results[idx]
            original = texts[idx]
 
            if len(result) is not 0:
                scrubbed = clean_text(text=original,
                                      findings=result)
                cleaned.append(scrubbed)
            else:
                cleaned.append(original)
        return cleaned
