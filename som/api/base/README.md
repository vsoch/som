# SOM API

This is a python wrapper for the School of Medicine (SOM) API. Currently, the base endpoint and latest version are 

      
      api_base = "https://api.rit.stanford.edu/identifiers/api"
      api_version = "v1"


If you need specific details about the endpoints or implementations, please see our [Swagger Specification](https://app.swaggerhub.com/api/susanweber/UID/1.0.0).

We expect to write a formal "getting started" guide when the development is finished, and for now we will include some quick "important to know" things.


## Important ToKnows
- If you are looking to give a set of identifiers (MRN) and get de-identified stuffs back, then there are two ways to go about this. 
  - For the first, you will want to save records to the database. This could be in the way of new `custom_fields` or any other inputs that come with your data. If you want to save records to the database, you will want to use the `identifiers/api/v1/uid/:study` endpoint.
  - For the second, you might just want a "lookup" functionality. E.g., here are my MRNs, please give me back what you know. In this case, you want the `identifiers/api/v1/mrn/:study` endpoint. This endpoint merely returns validation information (so could also be used as a testing endpoint), and no server state is changed by invoking it. Notice the difference is that the first uses `uid` (to save records) and the second uses `mrn` (to lookup records).


## Endpoint study examples
A "study" can be thought of an endpoint that might be specific to a function of interest. For example, right now we have studies `test` and `radiologydeid`. 

### test
You might want to test the functionality of the identifiers endpoint, both for saving and note saving data (and given test, no data will be saved):

      https://api.rit.stanford.edu/identifiers/api/v1/uid/test 
      https://api.rit.stanford.edu/identifiers/api/v1/mrn/test


### radiologydeid
When you are done with development and ready for production, you would use `radiologydeid` as your endpoint. There likely will be other study endpoints (this is the only one that we've developed for radiology thus far) but the idea is that you might want to save records that are specific to a study. For radiology that means an entity and list of items. The endpoint to save records for radiology queries would be:


      https://api.rit.stanford.edu/identifiers/api/v1/uid/radiologydeid 


or the equivalent to deidentify and retrieve the identifiers but not save any records.

      https://api.rit.stanford.edu/identifiers/api/v1/mrn/radiologydeid 


Again, the fact that this endpoint is not `test` means that it is for production data.


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

- [client.py](client.py): is the core client to communicate with the API. Each study can use it's proper module (for example, radiology has a [radiology.py](radiology.py) module that adds functions specific for the domain.
- [base.py](base.py): contains the default (current) endpoint and version of the API, along with core functions that are used across modules. Currently, we don't use many of these functions, and likely I'll be removing/adjusting some.
- [validators](validators): contains functions (for [requests](validators/requests.py) and [responses](validators/responses.py), respectively) that serve only to validate json data structures that are intended to go into POSTs. If a data structure is valid, True is returned. If not, False is returned, and the debugger prints why the structure is not valid for the user.
- [standards.py](standards.py): Within validation, there are certain fields that must match a particular pattern, be required, etc. This file holds lists/sets of items that are to be used as defaults for some of these items. The user has the option to define these lists with the validator functions, and if not defined, the defaults in this file are used. For example.
- [connect.py](connect.py): contains the `ApiConnection` that manages tokens, refreshing, and making calls. This object is created and held for use by the client.


## Study Modules
Under study, we have different study modules that might have custom functionality. For example:

- [radiology.py](radiology.py): Includes functions to post messages that have a person identifier and sets of items, in this case, a list of images to be de-identified. Currently, this function only serves to customize the study name, however specific functions for radiology can be added here.
