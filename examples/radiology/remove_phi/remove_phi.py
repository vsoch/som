#!/bin/env python

# This is an example script to use the SOM client endpoint for
# Google's "Data Loss Prevention" (DLP) API that does simple
# identification of finding phone numbers, etc. in texty things. 
# The text entities are submitted as a single string or list, and
# submit to the endpoint in batches of 100.

from som.api.google.dlp.client import DLPApiConnection

# This is creating the API client
dlp = DLPApiConnection()

# Here are some text "reports" with data
texts = ["The secret phone number is (603) 333-4444", # found
         "(603) 333-4444 is the number to call!",     # found
         "(603) 333-4444 is the name of the game.",   # found
         "Why hello, Dr. Xavier Zanderpuss.",         # not found
         "Dr. John Smith will be performing the task!",
         "The MRN is 1234567."]

# We can use dlp.inspect to find complete metadata about findings
findings = dlp.inspect(texts=texts)

'''
[{'findings': [{'createTime': '2017-03-22T18:05:04.937Z',
    'infoType': {'name': 'PHONE_NUMBER'},
    'likelihood': 'VERY_LIKELY',
    'location': {'byteRange': {'end': '41', 'start': '27'},
     'codepointRange': {'end': '41', 'start': '27'}},
    'quote': '(603) 333-4444'}]},
 {'findings': [{'createTime': '2017-03-22T18:05:04.949Z',
    'infoType': {'name': 'PHONE_NUMBER'},
    'likelihood': 'LIKELY',
    'location': {'byteRange': {'end': '14'}, 'codepointRange': {'end': '14'}},
    'quote': '(603) 333-4444'}]},
 {'findings': [{'createTime': '2017-03-22T18:05:04.942Z',
    'infoType': {'name': 'PHONE_NUMBER'},
    'likelihood': 'LIKELY',
    'location': {'byteRange': {'end': '14'}, 'codepointRange': {'end': '14'}},
    'quote': '(603) 333-4444'}]},
 {},
 {},
 {}]

'''

# And dlp.remove_phi to remove it from the text
cleaned = dlp.remove_phi(texts=texts)

# Yes, phi is probably not the most accurate description, 
# but it's not clear what level of de-id this will support,
# so let's start with that goal.


'''
['The secret phone number is **PHONE_NUMBER**',
 '**PHONE_NUMBER** is the number to call!',
 '**PHONE_NUMBER** is the name of the game.',
 'Why hello, Dr. Xavier Zanderpuss.',
 'Dr. John Smith will be performing the task!',
 'The MRN is 1234567.']
'''
