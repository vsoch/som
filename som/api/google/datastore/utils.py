'''
google/datastore.py: general storage utility functions

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from google.cloud import datastore as ds
from google.cloud.datastore.key import Key
from som.logger import bot
import sys
import os


######################################################################################
# Datastore Utils
######################################################################################

def parse_keys(client,keys):
    '''parse_keys will take in a list of keys, either just single model key
    names, or lists with a model and specific identifier, and return
    client.key objects
    '''
    for key in keys:
        if isinstance(key,list):
            keys.append(client.key(key[0],key[1]))
        else:
            keys.append(client.key(key))
        return keys


def get_key_filters():
    return ['<','>','=','<=','>=']


def print_datastore_path(name):
    '''print_datastore path will print a complete uri for a datastore
    object, like Entity1:key1/Entity2/key2
    '''
    if isinstance(name,Key):
        name = list(name.flat_path)
    parts = [ name[i:i+2] for i in range(0, len(name), 2) ]
    return "/".join([":".join(x) for x in parts])


######################################################################################
# Testing/Retry Functions
######################################################################################

def stop_if_result_none(result):
    '''stop if result none will return True if we should not retry 
    when result is none, False otherwise using retrying python package
    '''
    do_retry = result is not None
    return do_retry



