# coding: utf-8

"""
    Unique ID

    API to look up or generate a unique study identifier

    OpenAPI spec version: 1.0.0
    Contact: scweber@stanford.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import os
import sys
import unittest

import swagger_client
from swagger_client.rest import ApiException
from swagger_client.apis.developers_api import DevelopersApi


class TestDevelopersApi(unittest.TestCase):
    """ DevelopersApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.developers_api.DevelopersApi()

    def tearDown(self):
        pass

    def test_uid(self):
        """
        Test case for uid

        Accepts a list of identified items, returns a list of study specific identifiers
        """
        pass


if __name__ == '__main__':
    unittest.main()