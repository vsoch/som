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

        if study is None:
            study = "test"
        bot.info("Client: <study:%s>" %(study))
        self.base = api_base
        self.version = api_version
        self.study = study
        self.spec = spec
        self.token = token
        super(Client, self).__init__()

    def __str__(self):
        return "Client: <study:%s>" %(self.study)

    def __repr__(self):
        return "Client: <study:%s>" %(self.study)


    def deidentify(self,ids,study=None):
        '''deidentify: uid endpoint: 
         https://api.rit.stanford.edu/identifiers/api/v1/uid/{study} 
         will take a list of identifiers, and return the deidentified.        
        :param ids: a list of identifiers
        :param study: if None, defaults to test.
        '''    
        # Testing overrides all other specifications
        if study is None:
            study = self.study
        study = study.lower()

        # Did the user provide a valid study id?
        if study not in studies:
            bot.error("%s is not a valid study. Valid ids include %s" %(study,",".join(studies)))
            sys.exit(1)

        bot.debug("study: %s" %study)

        url = "%s/%s/uid/%s" %(self.base,
                              self.version,
                              study)

        return self.post(url=url,data=ids)
