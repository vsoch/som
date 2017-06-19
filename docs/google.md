# Google Storage and Datastore
At this point, you've likely used the DASHER endpoint to de-identify (code identifiers with an alias) some dicom dataset, you've queried the endpoint using the [identifiers](identifiers.md) client, and now you want to move the data into storage. As a reminder, you will get back a data structure from DASHER that looks like this:

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

and it's up to you to parse over that data structure and use it to de-identify the headers (likely by formatting it and giving it to [deid](https://pydicom.github.io/deid) and then you will have a de-identified dataset for Google Storage and Google Datastore. Let's go through the steps of doing this upload.

## Credentials
In order to use any Google product, you need to have the variable `GOOGLE_APPLICATION_CREDENTIALS` pointing to a file with your [default application credentials](https://developers.google.com/identity/protocols/application-default-credentials) exported in the environment. It's not going to work if you don't. If you do this from within Python, you can do:

```
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/vanessa/.topsecret/google"
```

you can also just export, for example, in your `~/.profile` or `~/.bashrc` or `~/.bash_profile`

```
GOOGLE_APPLICATION_CREDENTIALS=$HOME/.topsecret/google
export GOOGLE_APPLICATION_CREDENTIALS
```

## Google Storage

### Client
You probably want to start by making a client. Do that like this:

```
from som.api.google.storage import Client
client = Client(bucket_name='radiology')
```

The client is named based on your bucket

```
$ client
storage.google.radiology
```

Next, it's important to understand the structure that we will be creating, specifically, a Collection (study) that has some number of entities (coded patients) each of which have some number of images. This is an object storage so these aren't technically file paths, but you can think of them as such:


```
Collection / [ collection name ]/ Entity / [ entity name ] / Images / [ image name ]
Collection / Study / Entity / SUID123 / Images / suid123-1.dcm
```

For our purposes, if we are interested in a clinical study, it might make sense to name it based on the IRB number.

```
collection = client.create_collection(uid='IRB41449')
```

** still being written, tested, etc. **
