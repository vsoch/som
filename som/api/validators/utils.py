#!/usr/bin/env python

'''
validators/utils.py: utility functions for validators

'''

from som.logman import bot
import os
import sys

def validate_fields(acceptable_fields,actual_fields):
    '''validate_fields checks that there are not any in actual_fields
    that are not in acceptable_fields
    '''
    checking = [x for x in actual_fields if x not in acceptable_fields]
    if len(checking) == 0:
        return True
    bot.logger.error("Fields not allowed: ",", ".join(checking))
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
            bot.logger.error("Mismatch in length of source (%s) and comparator (%s). Exiting",
                                                               len(source),len(comparator))
            sys.exit(1)
    else:
        # Otherwise, we assume a common source
        universal_source = id_sources
    return universal_source
