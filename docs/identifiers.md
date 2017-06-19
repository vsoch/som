# Identifiers API
The identifiers API is a component of DASHER, and is limited in use to the Stanford School of Medicine. Currently, the endpoint and latest version are:

```      
api_base = "https://api.rit.stanford.edu/identifiers/api"
api_version = "v1"

```

If you need specific details about the endpoints or implementations, please see our [Swagger Specification](https://app.swaggerhub.com/api/susanweber/UID/1.0.0).

# Usage

## Authentication
Authentication works by way of a token/refresh token strategy. The file [auth.py](../som/api/base/auth.py) contains functions to drive this. As a user, you are given a refresh token, and you use it when needed to obtain an access token. How often is this? They expire after 24 hours, at which point a 401 response is issued, and the previous token is issued as the refresh token to get a new one. This is handled internally by the API, so the user (you) will just see a message like this:

```
response = client.deidentify(ids=identifiers)
DEBUG study: test
DEBUG POST https://api.rit.stanford.edu/identifiers/api/v1/uid/test
WARNING Expired token, refreshing...
Successfully refreshed access token.
DEBUG Headers found: Content-Type,Authorization
```

Where do the tokens come from? We don't have an automated way of doing this, so likely you will receive this file interally. The client would receive a `json` file to put in a secure place where he or she intends to use the API. It looks like this:
 
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

Thus, to answer the question above, the application can find and work with the tokens by way of this environment variable pointing to the file.

## Client
The first thing that you usually want to do is create a client. That looks like this:

```
from som.api.identifiers import Client
```

Notice that we have also imported a validators module, so we can validate data structures are correct before sending them. We can now instantiate the client:

```
client = Client()
# Client: <study:test>
```

Notice that since we did not define a study name, it defaults to `test`. 

## Example IDS Data Structure
For this example, we probably want to load some data. We provide a data structure of already extracted identifiers (so you don't need to start from nothing) so you can test it out.

```
from som.utils import (
    read_json,
    get_dataset
)

identifiers = read_json(get_dataset('developers_uid'))
```

The function `get_dataset` has different keys for datasets that are available. If you aren't sure what is available, just run it without arguments.

```
get_dataset()
Valid datasets include: developers_uid
```

We will add additional datasets that are needed to test endpoints as they are needed. Next, let's look at our identifiers:

```
{
   "identifiers":[
      {
         "id_timestamp":"1961-07-27T00:00:00Z",
         "id_source":"Stanford MRN",
         "id":"14953772",

         "custom_fields":[
            {
               "value":"MICKEY",
               "key":"firstName"
            },
            {
               "value":"MOUSE",
               "key":"lastName"
            }
         ],

         "items":[
            {
               "id_timestamp":"2010-02-04T11:50:00Z",
               "id_source":"Lab Result",
               "id":"MCH",
               "custom_fields":[
                  {
                     "value":"33.1",
                     "key":"ordValue"
                  }
               ]
            }
         ],

      }
   ]
}
```

While this example has only provided one entity with id `14953772` and one item, notice that items is a list, so you would send multiple items in batches. Also notice that the entire `identifiers` object is a list, and you could provide more than one entity at once. 

## Validation
We encourage you to validate your data structures before trying to send them to the API. If you send an invalid data structure, you are just adding errors to the layer cake. Validation looks like this:

```
from som.api.identifiers import validators

validators.validate_identifiers(identifiers)
# DEBUG Headers found: Content-Type
# DEBUG Headers found: Content-Type,Authorization
# DEBUG identifier MCH data structure valid: True
# DEBUG Identifiers data structure valid: True
# Out[2]: True
```


## Deidentify

Finally, let's deidentify! Note that you **must** be on Stanford VPN for this to work properly. If you aren't, you will see this:

```
response = client.deidentify(ids=identifiers)
DEBUG study: test
DEBUG POST https://api.rit.stanford.edu/identifiers/api/v1/uid/test
ERROR The server returned a malformed response. Are you on VPN?
```

After VPN, you should see a successful response:

```
# https://api.rit.stanford.edu/identifiers/api/uid
response = client.deidentify(ids=identifiers)
DEBUG study: test
DEBUG POST https://api.rit.stanford.edu/identifiers/api/v1/uid/test
```

and your response will look like this:

```
$ response

{'results': [{'id': '14953772',
   'id_source': 'Stanford MRN',
   'items': [{'id': 'MCH',
     'id_source': 'Lab Result',
     'jitter': 5,
     'jittered_timestamp': '2010-02-09T11:50:00-0800',
     'suid': '12fb'}],
   'jitter': 5,
   'jittered_timestamp': '1961-08-01T00:00:00-0700',
   'suid': '12fa'}]}
```

You are now free to use this data to replace identifiers in your data, and upload somewhere. This application has fulfilled its core function.

Now that you are familiar with the identifiers API, learn more in the [api developer](identifiers-developer.md) docs, which will walk through some of the setup of the identifiers endpoint module.
