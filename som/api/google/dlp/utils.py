
'''
utils.py: helper functions for DLP api

'''


from som.logman import bot

import os
import sys


def paginate_items(items,size=100):
    '''paginate_items will return a list of lists, each of a particular max
    size
    '''
    groups = []
    for idx in range(0, len(items), size):
        group = items[idx:idx+size]
        groups.append(group)
    return groups


def clean_text(text,findings):
    '''clean_text will remove phi findings from a text object
    :param text: the original text sent to the content.inspect DLP endpoint
    :param findings: the full response for the text.
    '''
    if 'findings' in findings:
        for finding in findings['findings']:
            label = "**%s**" %finding['infoType']['name']
            # Note sure if this is best strategy, we can start with it
            text = text.replace(finding['quote'],label)
    return text


