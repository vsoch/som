'''

Copyright (c) 2017 Vanessa Sochat, All Rights Reserved

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

from .requester import RetryRequester
from som.logger import bot
import os
import sys



try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


def summary(project):
    '''summarize counts of collections, images, entities
    for a project'''

    bot.spinner.start()
    requester = RetryRequester(project=project)
    collections = requester.get_collection()
    images = requester.get_image()
    entities = requester.get_entity()
    bot.spinner.stop()
    bot.newline()

    bot.info('Collections: %s' %len(collections))
    bot.info('Images: %s' %len(images))
    bot.info('Entity: %s' %len(entities))


def search_collections(project, uid=None):
    '''search collections will search for a particular collection,
    or if no uid specified, return a complete list of collections.
    
    Parameters
    ==========
    project: the project name to search Datastore for. 
    uid: if specified, return a specific collection

    Returns
    =======
    collections: list of Google datastore Entity
    '''

    fields = None
    if uid is not None:
        fields = {'uid': uid }

    requester = RetryRequester(project=project)
    collections = requester.get_collection(filters=fields)

    for collection in collections:
        bot.info('Collection: %s' %collection['uid'])
        for key,val in collection.items():
            bot.custom(prefix=key, message=val)
        bot.newline()

    print('Found %s collections' %len(collections))
    return collections


def search_entity(project, filters=None):
    '''search entity will look for all or a subset of entities under one
    or more collections in Google Datastore
 
    Parameters
    ==========
    project: the google project to use
    filters: fields to filter the entity
    '''

    bot.spinner.start()
    requester = RetryRequester(project=project)
    entities = requester.get_entity(filters=filters)
    bot.spinner.stop()
    bot.newline()
    for entity in entities:
        bot.info('Entity: %s' %entity['uid'])
        for key,val in entity.items():
            bot.custom(prefix=key, message=val)
        bot.newline()
    bot.info("Found %s entities" %len(entities))



def search_image(project, filters=None):
    '''search image will look for all or a subset of images in Google Datastore
 
    Parameters
    ==========
    project: the google project to use
    fields: fields to filter the entity
    '''

    requester = RetryRequester(project=project)
    images = requester.get_image(filters=filters)

    for image in images:
        bot.info('Image: %s' %image['uid'])
        for key,val in image.items():
            bot.custom(prefix=key, message=val)
        bot.newline()

    bot.info("Found %s images" %len(images))

