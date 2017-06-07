'''
client.py: client for working with identifiers API

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

from som.api.base import SomApiConnection
from .standards import (
    spec,
    studies
)

from som.logger import bot
import sys
import os

api_base = "https://api.rit.stanford.edu/identifiers/api"
api_version = "v1"

class Client(SomApiConnection):

    def __init__(self, token=None, study=None):
 
        self.base = api_base
        self.version = api_version
        self.study = study
        self.spec = spec
        self.token = token
        super(Client, self).__init__()


    def deidentifiy_update(self,identifiers,test=False):
        '''deidentify update calls deidentify, but setting save_records
        to True to ensure that data is updated/written.
        '''
        return self.deidentify(identifiers,test=test,save_records=True)


    def deidentify(self,ids,test=False,save_records=False):
        '''deidentify will take a list of identifiers, and return the deidentified.
        if save_records is True, will save records. If False (default) only
        returns identifiers.
        :param identifiers: a list of identifiers
        '''    

        # Saving records (uid) or not (mrn) changes the endpoint
        if save_records == True:
            action = "uid"
            bot.debug("[uid]: save_records is %s, no new data will be saved.")
        else:
            action = "mrn"
            bot.debug("[mrn]: save_records is %s, data will be saved.")

        # Testing overrides all other specifications
        study = self.study
        if test == True or study is None:
            study = 'test'
        study = study.lower()

        # Did the user provide a valid study id?
        if study not in studies:
            bot.error("%s is not a valid study. Valid ids include %s" %(study,",".join(studies)))
            sys.exit(1)

        bot.debug("study: %s" %study)

        url = "%s/%s/%s/%s" %(self.base,
                              self.version,
                              action,study)

        response = self.call(url=url,
                             data=ids,
                             func=self.post)

        if "results" in response:
            return response['results']
        return response
