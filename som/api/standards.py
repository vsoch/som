#!/usr/bin/env python

'''
standards.py: lists of standard things to be used with validators

'''

from som.logman import bot

# Sources (lists) of valid identifiers
identifier_sources = ['stanford','Stanford MRN', 'StanfordMRN']
item_sources = ['pacs','Stanford PACS', 'GE PACS', 'GE PACS Accession Number']

# Swagger api
spec = "https://app.swaggerhub.com/apiproxy/schema/file/susanweber/UID/1.0.0/swagger.json"

# Regular expressions
timestamp = '\d{4}-\d{2}-[A-Za-z0-9]{5}:\d{2}:\d{2}.[A-Za-z0-9]{4}$'
