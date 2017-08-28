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

from som.api.google.storage import Client
from retrying import retry

########################################################################
# RETRY FUNCTIONS
#----------------------------------------------------------------------
# exponential backoff for Google Cloud APIs that can have hiccups from
########################################################################

class RetryRequester:

    def __init__(self, bucket_name=None, project=None, client=None):
        self.client = client
        if project is not None:
            self.get_client(bucket_name,project)

    def __str__(self):
        if self.client is not None:
            return str(self.client)
        return self

    def __repr__(self):
        return self.__str__()


    # Create ----------------------------------------------------------------------------------------

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
    def create_collection(self, collection_name):
        return self.client.create_collection(collection_name)


    # Get ----------------------------------------------------------------------------------------

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
    def get_collection(self, filters=None):
        return self.get('Collection', filters)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
    def get_entity(self, filters=None):
        return self.get('Entity', filters)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
    def get_image(self, filters=None):
        return self.get('Image', filters)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
    def get(self, kind, filters=None):
        return self.client.batch.query(kind=kind,
                                       filters=filters)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
    def get_client(self, bucket_name,project):
        self.client = Client(bucket_name=bucket_name,
                             project_name=project)
        return self.client

    # Download ----------------------------------------------------------------------------------------

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=5)
    def download(self, blob, file_name):
        blob.download_to_filename(file_name)
