#!/usr/bin/env python

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

from som.logger import bot
import argparse
import sys
import os

def get_parser():
    parser = argparse.ArgumentParser(description="Stanford Open Modules for Python [SOM]")


    # Global Variables
    parser.add_argument("--version", dest='version', 
                        help="show software version", 
                        default=False, action='store_true')


    parser.add_argument('--debug', dest="debug", 
                        help="use verbose logging to debug.", 
                        default=False, action='store_true')


    subparsers = parser.add_subparsers(help='google storage and datastore',
                                       title='actions',
                                       description='actions for som tools',
                                       dest="command")


    # List (download)
    ls = subparsers.add_parser("list", 
                               help="list collections, entities, images.")


    ls.add_argument('--project', dest="project",
                     help="name of Google Cloud project (eg, som-irlearning)",
                     type=str, required=True)

    ls.add_argument("--images", dest='images', 
                    help="list image objects", 
                    default=False, action='store_true')

    ls.add_argument("--collections", dest='collections', 
                    help="list collection objects", 
                    default=False, action='store_true')

    ls.add_argument("--entity", dest='entity', 
                    help="list entity objects", 
                    default=False, action='store_true')

    ls.add_argument("--filters", dest='filters', nargs='+',
                    help="one or more filters, in key,operator,value PatientSex,=,F", 
                    type=str, default=None)

    # Get (download)
    get = subparsers.add_parser("get", 
                                help="download data from storge and datastore")

    get.add_argument("--outfolder", dest='outfolder', 
                     help="full path to folder for output, stays in tmp (or pwd) if not specified", 
                     type=str, default=None)

    get.add_argument('--project', dest="project",
                     help="name of Google Cloud project (eg, irlhs-learning)",
                     type=str, required=True)

    get.add_argument('--suid', dest="suid",
                     help='''An suid associated with an entity to find images (default) 
                             or query single images (set flag --query-images for the study. 
                             Typically begins with IRXXXX''',
                     type=str, required=True)

    get.add_argument('--query-images', dest="query_images", 
                        help="use verbose logging to debug.", 
                        default=False, action='store_true')

    get.add_argument('--bucket', dest="bucket",
                     help="Name of the storage bucket. Eg (irlhs-dicom)",
                     type=str, required=True)

    get.add_argument("--collection", dest='collection', 
                     help="name of collection (eg, IRB33192)", 
                     type=str, required=True)
    

    return parser


def get_subparsers(parser):
    '''get_subparser will get a dictionary of subparsers, to help with printing help
    '''
    actions = [action for action in parser._actions 
               if isinstance(action, argparse._SubParsersAction)]

    subparsers = dict()
    for action in actions:
        # get all subparsers and print help
        for choice, subparser in action.choices.items():
            subparsers[choice] = subparser

    return subparsers



def main():

    parser = get_parser()
    subparsers = get_subparsers(parser)

    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    # if environment logging variable not set, make silent
    if args.debug is False:
        os.environ['MESSAGELEVEL'] = "5"

    if args.version is True:
        from som.version import __version__
        print(__version__)
        sys.exit(0)


    if args.command == "list":
        filters = args.filters
        if filters is not None:
            fields = []
            for filterset in filters:
                key,oper,val=filterset.split(',')
                bot.info("Adding filter %s%s%s" %(key,oper,val))                  
                fields.append((key, oper, val))
            filters = fields

        if args.entity is True:
            from .search import search_entity
            search_entity(project=args.project,
                          filters=filters)
            sys.exit(0)
        if args.collections is True:
            from .search import search_collections
            search_collections(project=args.project)
            sys.exit(0)
        if args.images is True:
            from .search import search_image
            search_image(project=args.project,
                         filters=filters)
            sys.exit(0)
        from .search import summary
        summary(project=args.project)
        sys.exit(0)

    if args.command == "get":
        from .get import download_collection 
        output_folder = download_collection(output_folder=args.outfolder,
                                            collection=args.collection,
                                            project=args.project,
                                            suid=args.suid,
                                            query_entity=not args.query_images,
                                            bucket=args.bucket)
        sys.exit(0)

    parser.print_help()

if __name__ == '__main__':
    main()
