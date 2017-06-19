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

### Create a Collection
A collection is a logical grouping of entities, usually associated with something like a study, or for publishing, a journal. For our purposes, if we are interested in a clinical study, it might make sense to name it based on the IRB number.

```
collection = client.create_collection(uid='IRB41449')
```


### De-identify
This is largely up to you, but for the example let's load some dummy data from [deid](https://pydicom.github.io/deid):

```
from deid.data import get_dataset
from deid.dicom import get_files
dicom_files = get_files(get_dataset('dicom-cookies'))
```

And let's properly de-identify them!

```
from deid.dicom import get_identifiers, replace_identifiers

ids=get_identifiers(dicom_files)
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
DEBUG Found 27 defined fields for image4.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG Found 27 defined fields for image2.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG Found 27 defined fields for image7.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG Found 27 defined fields for image6.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG Found 27 defined fields for image3.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG Found 27 defined fields for image1.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
DEBUG Found 27 defined fields for image5.dcm

updated_files = replace_identifiers(dicom_files=dicom_files,
                                    ids=ids)
```

### Create an Entity
An entity within a collection corresponds to one patient. In this exanple above, we have 7 dicom images, but only for one patient. For example, here is his id in the `ids` data structure:

```
ids.keys()
dict_keys(['cookie-47'])
```

Let's make an entity for this cookie! First, we would have some loop or process to make a dictionary of metadata for the entity. This would correspond to things like a jittered date, or any custom fields you want stored with the entity. We recommend taking an approach that tries to answer the question "How would someone search for, and then find it?" We want to have meaningful fields and values that can answer that question. Some of the fields might come from the (de-identified) data that would be useful to search for, like study alias, image modality, etc. Here is an example:


```
metadata = { "source_id" : "cookieTumorDatabase",
             "id":"cookie-47",
             "Modality": "cookie"}
```

Then making the call coincides with creating a dataset. One Entity with images and metadata within a collection is considered a dataset.

```
client.upload_dataset(images=updated_files,
                      collection=collection,
                      uid=metadata['id'],
                      metadata=metadata)
```

** still under development, more to come **
