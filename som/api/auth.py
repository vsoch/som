#!/usr/bin/env python

'''
auth.py: authentication functions for som api

'''

from som.logman import bot
from som.api.utils import (
    api_base,
    api_get,
    api_post,
    api_put,
    api_version
)

from som.utils import (
    read_file
)

import os
import sys


def authenticate(domain=None,token_folder=None):
    '''authenticate will authenticate the user with the SOM api. This means
    either obtaining the token from the environment, and then trying to obtain
    the token file and reading it, and then finally telling the user to get it.
    :param domain: the domain to direct the user to for the token, default is api_base
    :param token_folder: the location of the token file, default is $HOME (~/)
    '''

    # Attempt 1: Get token from environmental variable
    token = os.environ.get("STANFORD_SOM_TOKEN",None)

    if token == None:
        # Is the user specifying a custom home folder?
        if token_folder == None:
            token_folder = os.environ["HOME"]

        token_file = "%s/.somapi" %(token_folder)
        if os.path.exists(token_file):
            token = read_file(token_file)[0].strip('\n')
        else:
            if domain == None:
                domain = api_base
            print('''Please obtain token from %s/token
                     and save to .somtoken in your $HOME folder''' %(domain))
            sys.exit(1)
    return token


def get_headers(token=None):
    '''get_headers will return a simple default header for a json
    post. This function will be adopted as needed.
    :param token: an optional token to add for auth
    '''
    headers = dict()
    headers["Content-Type"] = "application/json"
    if token!=None:
        headers["Authorization"] = "Bearer %s" %(token)

    header_names = ",".join(list(headers.keys()))
    bot.logger.debug("Headers found: %s",header_names)
    return headers
