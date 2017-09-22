#!/usr/bin/env python

'''

client.py: simple clients for google sheets. Requires the environment variable GOOGLE_APPLICATION_CREDENTIALS

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

import datetime
from apiclient import discovery
from .utils import get_google_service
from som.api import ApiConnection
from som.logger import bot


class Client(ApiConnection):

    def __init__(self,**kwargs):
        self.cli = get_google_service()
        super(ApiConnection, self).__init__(**kwargs)


    def read_spreadsheet(self, sheet_id, range_name="A:Z"):
        '''read spreadsheet will read a spreadsheet based on an id.
        '''
        result = self.cli.spreadsheets().values().get(
                          spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        return values
