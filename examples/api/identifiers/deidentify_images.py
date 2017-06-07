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
validate_identifiers(identifiers)
# In [8]: validate_identifiers(identifiers)
# DEBUG identifier A654321 data structure valid: True
# DEBUG identifier B654321 data structure valid: True
# DEBUG Identifiers data structure valid: True
# Out[8]: True

# Note that you must be on Stanford VPN
# deidentify(identifiers,test=False,save_records=False)
response = client.deidentify(ids=identifiers) # Default uses mrn endpoint, doesn't save
