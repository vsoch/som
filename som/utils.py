#!/usr/bin/env python

'''
utils.py: part of som package

'''

import collections
import os
import re
import requests

import shutil
import simplejson
import som.__init__ as hello
from som.logman import bot
import sys

import subprocess

import tempfile
import zipfile


# Python less than version 3 must import OSError
if sys.version_info[0] < 3:
    from exceptions import OSError


######################################################################################
# Local commands and requests
######################################################################################

def get_installdir():
    '''get_installdir returns the installation directory of the application
    '''
    return os.path.abspath(os.path.dirname(hello.__file__))


def run_command(cmd,error_message=None,sudopw=None,suppress=False):
    '''run_command uses subprocess to send a command to the terminal.
    :param cmd: the command to send, should be a list for subprocess
    :param error_message: the error message to give to user if fails, 
    if none specified, will alert that command failed.
    :param execute: if True, will add `` around command (default is False)
    :param sudopw: if specified (not None) command will be run asking for sudo
    '''
    if sudopw == None:
        sudopw = os.environ.get('pancakes',None)

    if sudopw != None:
        cmd = ' '.join(["echo", sudopw,"|","sudo","-S"] + cmd)
        if suppress == False:
            output = os.popen(cmd).read().strip('\n')
        else:
            output = cmd
            os.system(cmd)
    else:
        try:
            process = subprocess.Popen(cmd,stdout=subprocess.PIPE)
            output, err = process.communicate()
        except OSError as error: 
            if error.errno == os.errno.ENOENT:
                bot.logger.error(error_message)
            else:
                bot.logger.error(err)
            return None
    
    return output


############################################################################
## FILE OPERATIONS #########################################################
############################################################################

def write_file(filename,content,mode="w"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename,mode) as filey:
        filey.writelines(content)
    return filename


def write_json(json_obj,filename,mode="w",print_pretty=True):
    '''write_json will (optionally,pretty print) a json object to file
    :param json_obj: the dict to print to json
    :param filename: the output file to write to
    :param pretty_print: if True, will use nicer formatting   
    '''
    with open(filename,mode) as filey:
        if print_pretty == True:
            filey.writelines(simplejson.dumps(json_obj, indent=4, separators=(',', ': ')))
        else:
            filey.writelines(simplejson.dumps(json_obj))
    return filename


def read_file(filename,mode="r"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename,mode) as filey:
        content = filey.readlines()
    return content
