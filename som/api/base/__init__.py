'''
som.base: the base connection to the SOM API

'''

from som.logman import bot

from som.api.base.auth import (
    authenticate,
    refresh_access_token
)

from som.api import ApiConnection

api_base = "https://api.rit.stanford.edu/identifiers/api"
api_version = "v1"

class SomApiConnection(ApiConnection):

    def __init__(self, token=None, **kwargs):
        super(SomApiConnection, self).__init__(**kwargs)
 
        self.headers = None
        if token is None:
            self.token = authenticate()
        else:
            self.token = token
        self.update_headers()
        

    def call(self,url,func,data=None,return_json=True):
        '''call overrides post for the som api to add the option
        to refresh a token given a 401 response.
        :param url: the url to send file to
        :param data: additional data to add to the request
        :param return_json: return json if successful
        '''
        response = func(url,self.headers,json=data)

        # Errored response, try again with refresh
        if response.status_code == 401:
            bot.logger.warning("Expired token, refreshing...")
            self.token = refresh_access_token()
            response = func(url,self.headers,json=data)

        if response.status_code == 200 and return_json:
            return response.json()

        return response
