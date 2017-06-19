#!/bin/env python

# This is an example of sending a list of identifiers to the API

from som.api.identifiers import (
    Client,
    validators
)

from som.utils import (
    read_json,
    get_dataset
)

client = Client()
# Client: <study:test>

identifiers = read_json(get_dataset('developers_uid'))
validators.validate_identifiers(identifiers)
# DEBUG Headers found: Content-Type
# DEBUG Headers found: Content-Type,Authorization
# DEBUG identifier MCH data structure valid: True
# DEBUG Identifiers data structure valid: True
# Out[2]: True

# Note that you must be on Stanford VPN
# https://api.rit.stanford.edu/identifiers/api/uid
response = client.deidentify(ids=identifiers)
