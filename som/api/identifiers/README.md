# Identifiers

This is the identifiers API for the School of Medicine, which is an instance of the [base](../base) API that implements basic authentication. Currently, the base endpoint and latest version are 

```      
api_base = "https://api.rit.stanford.edu/identifiers/api"
api_version = "v1"

```

If you need specific details about the endpoints or implementations, please see our [Swagger Specification](https://app.swaggerhub.com/api/susanweber/UID/1.0.0).

## Dicom
The folder called [dicom](dicom) is an example plugin/template that provides a set of rules for how the API should read, and deal with identifiers in a standard dicom image. The functions for doing so are in the file called [tasks.py](dicom/tasks.py), and the rules provided in the associated json data structure [config.json](dicom/config.json). This means that, as a user, you could use the functions but provide a different config.json with your own rules. As a developer, you can copy this folder for a different data type, and write the corresponding functions for your datatype. Please [post an issue](https://www.github.com/vsoch/som/issues) if you have questionsor need help with this task.


## What would you use this client for?
- If you are looking to give a set of identifiers (MRN) and get de-identified stuffs back, then there are two ways to go about this. 
  - For the first, you will want to save records to the database. This could be in the way of new `custom_fields` or any other inputs that come with your data. If you want to save records to the database, you will want to use the `identifiers/api/v1/uid/:study` endpoint.
  - For the second, you might just want a "lookup" functionality. E.g., here are my MRNs, please give me back what you know. In this case, you want the `identifiers/api/v1/mrn/:study` endpoint. This endpoint merely returns validation information (so could also be used as a testing endpoint), and no server state is changed by invoking it. Notice the difference is that the first uses `uid` (to save records) and the second uses `mrn` (to lookup records).

## Endpoint study examples
A "study" can be thought of an endpoint that might be specific to a function of interest. For example, right now we have studies `test` and `radiologydeid`. The valid study names are provided in [standards.py](standards.py). If there is a new study added, it must be added here.


### test
You might want to test the functionality of the identifiers endpoint, both for saving and note saving data (and given test, no data will be saved):

```
https://api.rit.stanford.edu/identifiers/api/v1/uid/test 
https://api.rit.stanford.edu/identifiers/api/v1/mrn/test
```

### radiologydeid
When you are done with development and ready for production, you would use `radiologydeid` as your endpoint. There likely will be other study endpoints (this is the only one that we've developed for radiology thus far) but the idea is that you might want to save records that are specific to a study. For radiology that means an entity and list of items. The endpoint to save records for radiology queries would be:

```
https://api.rit.stanford.edu/identifiers/api/v1/uid/radiologydeid 
```

or the equivalent to deidentify and retrieve the identifiers but not save any records.

```
https://api.rit.stanford.edu/identifiers/api/v1/mrn/radiologydeid 
```

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

```
export STANFORD_CLIENT_SECRETS="/home/clientname/.allthesecrets/som-stanford.json"
```

- [client.py](client.py): is the core client to communicate with the API, which extends the `SomApiConnection` under [base](../base). The client can take a specific study (valid defined in [standards.py](standards.py) or it not provided, will default to `test`.
- [standards.py](standards.py): Contains valid study names, along with the url of the swagger specification for the API.

