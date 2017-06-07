#!/usr/bin/env python

'''
validators/utils.py: utility functions for validators

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


from som.logger import bot
import os
import sys

def validate_fields(acceptable_fields,actual_fields):
    '''validate_fields checks that there are not any in actual_fields
    that are not in acceptable_fields
    '''
    checking = [x for x in actual_fields if x not in acceptable_fields]
    if len(checking) == 0:
        return True
    bot.error("Fields not allowed: %s" %", ".join(checking))
    return False


def get_universal_source(source,comparator):
    '''get universal source will, given a source item (a list or single item), check to
    see if the length of a comparator is equivalent. The comparator is expected to be a list
    the same length as the source.
    :param source: the source item (single item or list)
    :param comparator: the thing to compare to
    :returns: EITHER a universal source (meaning one item to use for all items in source) OR None,
    meaning the comparator should be treated as a list, and source[i] matched to comparator[i]
    '''
    universal_source = None
    if isinstance(source,list):
        if len(source) != len(comparator):
            bot.error("Mismatch in length of source (%s) and comparator (%s). Exiting"
                                                            %(len(source),len(comparator)))
            sys.exit(1)
    else:
        # Otherwise, we assume a common source
        universal_source = id_sources
    return universal_source
