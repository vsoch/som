#!/usr/bin/env python

'''
wordfish.base.py: base module for working with wordfish standard

'''

from som.logman import bot

from som.utils import (
    get_installdir, 
    read_file, 
    write_file
)

from som.wordfish.validators import (
    validate_folder,
    validate_compressed
)

import subprocess
import tempfile
import zipfile
import inspect
import shutil
import requests
import imp
import sys
import re
import os


def run_validation(inputs,test_dir=None,clean_up=True,fail_exit=True):
    '''run validation will run one or more inputs through the validation procedure,
    meaning checking that the folder (and other data structures) fit the WordFish
    standard: http://www.github.com/radinformatics/wordfish-standard
    :param inputs: a single, or list of inputs, meaning folders and compressed files 
    for validation
    :param test_dir: a directory to use to extract and run things. If not specified,
    one is created.
    :param clean_up: boolean to determine if test_dir and subcontents should be
    removed after tests. Default is True.
    :param fail_exit: Given failure of validation, fail the process. Otherwise, return
    False to the calling function. Default fail_exit is True
    '''
    if not isinstance(inputs,list):
        inputs = [inputs]

    bot.logger.debug("Found %s inputs to test using som-validator.", len(inputs))
    
    # Where are we testing?
    if test_dir == None:
        test_dir = tempfile.mkdtemp()

    # Tell the user about testing folder
    message = "Testing folder will be %s"
    if clean_up == True:
        message = "%s, and will be removed upon completion." %(message)
    bot.logger.debug(message, test_dir)

    for testing in inputs:
        if os.path.isdir(testing):
            valid = validate_folder(folder=testing)
        elif re.search("[.]zip$|[.]tar[.]gz$",testing):
            valid = validate_compressed(compressed_file=testing,
                                        testing_base=test_dir,
                                        clean_up=clean_up)

        # Always exit or return False if input is not valid
        if valid == False:
            if fail_exit == True:
                bot.logger.error("Input %s is not valid, please fix and retest. Exiting.", testing)
                sys.exit(1)
            bot.logger.error("Input %s is not valid, please fix and retest. Returning False.", testing)
            return valid

    return valid
