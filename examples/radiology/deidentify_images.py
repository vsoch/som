#!/bin/env python

# This is an example of sending a list of identifiers to the API


import os
import sys

from som.api.radiology import Client
from som.api.validators.requests import validate_identifiers
from som.utils import read_json

client = Client()
identifiers = read_json('../../som/api/tests/data/developers_uid.json')
validate_identifiers(identifiers)
response = client.deidentify(identifiers)

        self.assertTrue(isinstance(response,list))       

        # Validate response
        print("Case 3: Formatting of identifiers response is correct.")
        self.assertTrue(receive_identifiers(response))

        # Assert we have the same number of inputs and outputs
        print("Case 4: Response returns same number of identifiers as given, %s" %(len(response)))
        self.assertEqual(len(response),len(self.identifiers['identifiers']))


if __name__ == '__main__':
    unittest.main()
