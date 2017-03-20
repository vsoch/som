#!/usr/bin/env python

'''
auth.py: authentication functions for som api

'''


from som.logman import bot

from som.utils import (
    read_json,
    write_json
)

import os
import json
import requests
import sys


def read_client_secrets():
    secrets = None
    token_file = os.environ.get("STANFORD_CLIENT_SECRETS",None)
    if token_file is not None:
        if os.path.exists(token_file):
            secrets = read_json(token_file)
    if secrets is None:
        bot.logger.error('Cannot find STANFORD_CLIENT_SECRETS credential file path in environment.')
        sys.exit(1)
    return secrets


def authenticate():
    '''get_access_token will return the currently active access token
    from the client secrets file
    '''
    token = None
    secrets = read_client_secrets()
    if secrets is not None:
        token = secrets['accessToken']
    return token


def refresh_access_token():
    '''refresh access token reads in the client secrets from 
    the token file, and update the tokens, and save back to file
    '''
    token_file = os.environ.get("STANFORD_CLIENT_SECRETS",None)
    secrets = read_client_secrets()
    token = None

    # Query to update the token - must be on Stanford network
    if secrets is not None:
        response = requests.post(secrets['token_uri'],
                                 data={'refreshToken':secrets['refreshToken']},
                                 headers=get_headers())

        if isinstance(response,dict):
            secrets["accessToken"] = response['accessToken']
            secrets["refreshToken"] = response['refreshToken']
            print("Successfully refreshed access token.")
            token_file = write_json(secrets,token_file)
            token = secrets['accessToken']

    return token
