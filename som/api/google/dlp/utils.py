
'''
utils.py: helper functions for DLP api

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


