#!/usr/bin/env python

'''

cli.py: command line client for som (som-validator)

'''

from som.version import __version__
import optparse
import os
import re
import shutil
import sys
import tempfile

def get_parser():


    parser = optparse.OptionParser(description='validate folder and compressed file structures of text and images',
                                   usage="usage: %prog [options]",
                                   version=__version__)

    # Name of folder or zipped file to test. Not required
    parser.add_option("--test", 
                      dest='test', 
                      help="folder or file to run validation test on. If none supplied, will use $PWD as folder.", 
                      type=str, 
                      default=None)

    # Change level of verbosity
    parser.add_option("--quiet", 
                      dest='quiet', 
                      action="store_true",
                      help="don't print information about validation", 
                      default=False)

    # Detect zip files in folder insteaed
    parser.add_option("--detect-compressed", 
                      dest='detect_compressed', 
                      action="store_true",
                      help="look for zip/tar.gz files in present working directory, if --test not specified or empty", 
                      default=False)

    return parser


def main():
    '''main is a wrapper for the client to hand the parser to the executable functions
    This makes it possible to set up a parser in test cases
    '''
    parser = get_parser()
    
    try:
        (args,options) = parser.parse_args()
    except:
        sys.exit(0)

    # Give the args to the main executable to run
    run(args)


def run(args):

    print("--- starting som-validator ---")

    if args.quiet == True:
        os.environ['SOM_MESSAGELEVEL'] = "CRITICAL"

    from som.logger import bot
    from som.utils import detect_compressed
    from som.wordfish.base import run_validation

    # We will keep a list of testing folders/zips
    folders = []

    # What are we testing?
    if args.test not in [None,""]:

        # specify using compressed in folder?
        if args.detect_compressed == True:
            inputs = detect_compressed(folder=args.test)
            folders = folders + inputs

        # just use folder, present working directory
        else:
            folders = [args.test]

        # run the validation tests
        run_validation(inputs=folders) # test_dir = None
                                       # clean_up = True
                                       # fail_exit = True
    else:
        print("You must specify a folder or compressed object with --test.")

if __name__ == '__main__':
    main()
