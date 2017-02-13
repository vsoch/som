#!/bin/env python

# This is an example script to generate a list of identifiers to send to the api.

from som.api.base import (
    create_identifiers,
    create_items
)

#TODO: will write complete example with dummy data when API endpoint finished

from som.api.validation.requests import validate_identifiers

# Here is how to create items
items = create_items(item_ids=item_ids,
                     id_sources=item_id_sources,
                     sources=item_sources,
                     custom_fields=item_custom_fields,
                     verbose=True)

# Here is how to create an entity
entity = create_identifiers(entity_id=person_id,
                            id_source=person_id_source,
                            id_timestamp=id_timestamp,
                            items = items.
                            custom_fields=person_custom_fields) #verbose True

# And validate
validate_identifiers(entity)
