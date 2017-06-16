# SOM API Base

This is a python wrapper for the School of Medicine (SOM) API and this module (base) is a skeleton that implements the token authentication that specific SOM APIs (eg, [identifiers](../identifiers) can easily plug into.

## Main Modules
Content in the following files includes:

- [auth.py](auth.py): contains functions to authenticate a person with the API. We are taking a simplified Oauth approach, where a client is given a refresh token, and uses it when needed to obtain an access token. How often is this? They expire after 24 hours, at which point a 401 response is issued, and the client can issue the previous token as the refresh token to get a new one. We will likely make this more robust and use [oauth2client](https://oauth2client.readthedocs.io) but this simple approach works for now. Ideally, the client would authenticate with a stanford email address through some web portal, and be given a `json` file to download to a secure place:
 
     {
      'accessToken': 'ttttttuuuuuurrrrrrttttttlllllleeeee',
      'client_id': 'client.email@stanford.edu',
      'refreshToken': 'ttttttttttttttttttttttttuuuuuuuuuuuuuuuurrrrrrttttttllllllle',
      'token_uri': 'https://api.rit.stanford.edu/token/api/v1/refresh'
     }

The user would be instructed to add a line to his or her `.bashrc` or `.profile` to export the location of this file into an environmental variable, to be available to the application to discover the secrets:

       export STANFORD_CLIENT_SECRETS="/home/clientname/.allthesecrets/som-stanford.json"
