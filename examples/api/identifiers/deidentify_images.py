#!/bin/env python

# This is an example of sending a list of identifiers to the API


import os
import sys

from som.api.identifiers import Client
from som.api.base.validators import validate_identifiers
from som.utils import (
    read_json,
    get_dataset
)

client = Client()

identifiers = read_json(get_dataset('developers_uid'))


identifiers = read_json('../../som/api/base/tests/data/developers_uid.json')
validate_identifiers(identifiers)

# Note that you must be on Stanford VPN
# deidentify(identifiers,test=False,save_records=False)
response = client.deidentify(ids=identifiers) # Default uses mrn endpoint, doesn't save
