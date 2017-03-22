#!/bin/env python

# This is an example script to upload data (images, text, metadata) to
# google cloud storage and datastore. We use the wordfish standard,
# assuming the data has been de-identified. The first step 
# below we structure our dataset. This also validates that it's
# formatted correctly. In the second step, we use the radiology
# client to upload the structures to storage and datastore.


from som.api.google.dlp.client import DLPApiConnection

dlp = DLPApiConnection()

texts = ["The secret phone number is (603) 333-4444", # found
         "(603) 333-4444 is the number to call!",     # found
         "(603) 333-4444 is the name of the game.",   # found
         "Why hello, Dr. Xavier Zanderpuss.",         # not found
         "Dr. John Smith will be performing the task!",
         "The MRN is 1234567."]

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

cleaned = dlp.remove_phi(texts=texts)

'''
['The secret phone number is **PHONE_NUMBER**',
 '**PHONE_NUMBER** is the number to call!',
 '**PHONE_NUMBER** is the name of the game.',
 'Why hello, Dr. Xavier Zanderpuss.',
 'Dr. John Smith will be performing the task!',
 'The MRN is 1234567.']
'''
