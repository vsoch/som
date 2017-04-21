#!/usr/bin/env python

'''
base.py: base module for working with som api

'''

from som.logman import bot
from som.api.base import ClientBase

class Client(ClientBase):

    def __init__(self,**kwargs):
        super(Client, self).__init__(**kwargs)
        self.study = 'radiologydeid'
