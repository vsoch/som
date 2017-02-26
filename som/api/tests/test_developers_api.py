# coding: utf-8

'''
    Unique ID

    API to look up or generate a unique study identifier

    OpenAPI spec version: 1.0.0
    Contact: scweber@stanford.edu

'''

from __future__ import absolute_import

import os
import sys
import unittest

from som.api.radiology import Client
from som.api.validators.responses import receive_identifiers
from som.api.validators.requests import validate_identifiers
from som.utils import read_json

here = os.path.dirname(os.path.realpath(__file__))

class TestDevelopersApi(unittest.TestCase):
    """ DevelopersApi unit tests"""


    def setUp(self):
        self.client = Client()
        self.identifiers = read_json('%s/data/developers_uid.json' %(here))


    def tearDown(self):
        pass

    def test_uid(self):
        '''Test case for uid
        Accepts a list of identified items, returns a list of study specific identifiers
        '''

        print("Case 1: Formatting of identifiers input is correct.")
        self.assertTrue(validate_identifiers(self.identifiers))

        print("Case 2: Respones returns status 200, json object")
        response = self.client.deidentify(self.identifiers)
        self.assertTrue(isinstance(response,list))       

        # Validate response
        print("Case 3: Formatting of identifiers response is correct.")
        self.assertTrue(receive_identifiers(response))

        # Assert we have the same number of inputs and outputs
        print("Case 4: Response returns same number of identifiers as given, %s" %(len(response)))
        self.assertEqual(len(response),len(self.identifiers['identifiers']))


if __name__ == '__main__':
    unittest.main()
