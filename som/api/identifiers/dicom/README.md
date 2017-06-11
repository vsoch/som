# Dicom Identifiers Template
This folder contains an example processing template that tells the som api application how to process different header values for datatype DICOM. It should contain should contain the following files:

 - **config.json** this is the default specification for how a dicom header is mapped into a request to the identifiers API, and then the action to take for each header field on a response. A user can copy this file and change the values, and provide this copy to the functions to specify a custom behavior.
 - **__init__.py**: has the purpose of exposing module functions to the higher up folder for import. For example, the function `get_identifiers` in [tasks.py](tasks.py) is programatically accessible via `from som.api.identifiers.dicom import get_identifiers` thanks to this file. If you create a new module with the equivalent functions, you should be fine to just copy this file, or import the functions directly from tasks.py in the module folder.
 - **tasks.py**: should contain functions for `get_identifiers`, which should return a valid request to the som identifiers API, and `remove_identifiers`, which should accept a valid response, and one or more of the dataset type to remove from. This function should return a list of one or more objects that have been de-identified. Finally, this file should contain any custom functions needed by config.json

Note that, since we are working in Python, we will be using dicom headers that are mapped from the standard to pydicom, the entire mapping which is provided [here](https://github.com/pydicom/pydicom/blob/master/pydicom/_dicom_dict.py), and programatically accessible via:

```
from pydicom._dicom_dict import DicomDictionary

field_names = []

for key,entry in DicomDictionary.items():
   if entry[3] != "Retired":
       field_names.append(entry[4])
```

Since there are so many, it's recommended to have a conservative default for replacements (under section [Response](#Response) below, so you don't need to code every single field into the [config.json](config.json). Speaking of, let's talk about that.

## Config.json
The base of the json has two classes, and they correspond with the API actions of `request` and `response`. Here they are, completely empty:

```
{
 "request": {},
 "response": {}
}
```

### Requests
Requests require knowing how to generate a request to the API from a dicom dataset, or more specifically, how to get identifiers from the data. This means that we need to extract information about some entity and one or more items belonging to it, and this is why the fields under `requests` are `entity` and `item`. We can recall a traditional request made by the identifiers API:

```
{  
   "identifiers":[  
      {  
         "id":"14953772",
         "id_source":"Stanford MRN",
         "id_timestamp":"1961-07-27T00:00:00Z",
         "custom_fields":[  
            {  
               "key":"firstName",
               "value":"MICKEY"
            },
            {  
               "key":"lastName",
               "value":"MOUSE"
            }
         ],
         "items":[  
            {  
               "id":"MCH",
               "id_source":"Lab Result",
               "id_timestamp":"2010-02-04T11:50:00Z",
               "custom_fields":[  
                  {  
                     "key":"ordValue",
                     "value":"33.1"
                  }
               ]
            }
         ],
      }
   ]
}

```

The `entity` is referring to the main thing that has items belonging to it, corresponding to this section of an identifier:

```
      "id":"14953772",
         "id_source":"Stanford MRN",
         "id_timestamp":"1961-07-27T00:00:00Z",
         "custom_fields":[  
            {  
               "key":"firstName",
               "value":"MICKEY"
            },
            {  
               "key":"lastName",
               "value":"MOUSE"
            }
```

and it follows that an item maps on to one of the sections under `items`:

```
            {  
               "id":"MCH",
               "id_source":"Lab Result",
               "id_timestamp":"2010-02-04T11:50:00Z",
               "custom_fields":[  
                  {  
                     "key":"ordValue",
                     "value":"33.1"
                  }
               ]
            }

```

Thus, for the `request` section of any [config.json](config.json), we will have each of `entity` and `item`, and under both, each of the fields that the API needs to know how to parse from the data, meaning `id`, `id_source`, `id_timestamp`, and `custom_fields`. An empty data structure would look like this:

```
{

   "request": {
       "entity":{
          "custom_fields":{}
          "id":{},
          "id_source":{},
          "id_timestamp":{}
       },
       "item":{
          "custom_fields":{},
          "id":{},
          "id_source":{},
          "id_timestamp":{}
       }
    }
} 
```

The job of the configuration file is to tell the software how to deal with each of those fields for each attribute. Thus, we will be adding a dictionary with fields `type` and `value` under each of the attributes (id, id_source, custom_fields) shown above.

#### Defining Values
For any attribute with a type/value pair, type will correspond one of `default`, `data`,`env`, or `func`. A **default** means that the value provided should be used by default. In the example below, we will set `id_source` to be `PatientID` by default:

```
      "id_source":{
         "type":"default",
         "value":"PatientID"
      },

``` 

And it follows then that the id should come from the field in the header, `PatientID`. To do this, we would want to use a field from the header, and we can set the type to **data**. In the example below, we are setting the `id` to be the value `PatientID` that is provided in the header.


```
      "id":{
         "type":"data",
         "value":"PatientID"
      },

``` 

If we want to get a value set in the environment (retrieved via `os.environ`) then we can set the type to `env`, and the `value` should correspond to the name of the environment variable. For example, the following would set the `id_source` to be the variable `ID_SOURCE_DEFAULT` exported in the environment.


```
      "id":{
         "type":"env",
         "value":"ID_SOURCE_DEFAULT"
      },

``` 

Finally, it could be that we want to have some custom action that is not supported with such simple terms. A good example is generating a UTC timestamp from the Dicom data - we in fact need to use two dicom headers, and add a lot of custom operations to them. For this, we have the `func` type, and we should expect the function to be found in `tasks.py`.


#### Obtaining Identifiers
If you are writing a new data type module (eg, dicom), your function called `get_identifiers` in the [tasks.py](tasks.py) should understand how to take the [config.json](config.json) and the data structure (eg, a dicom file) and return a valid request to the API. For this default for dicom, I made this approach modular, meaning that the main function `get_identifiers` uses a helper function, `get_identifier`, to parse a configuration file paired with a dicom image and return the correct data. For example, let' say that we read in the config file:

```
from som.utils import read_json
config = read_json('config.json')['request']
```

Note that we are subsetting to the `request` section where the fields entity and item are. Then we have the following specification for the id:


```
      "id_source":{
         "type":"default",
         "value":"PatientID"
      },
```

and we've read in some dicom file with `pydicom.read_file`, let's call it `dicom`. We can then call the `get_identifier` function:

```
source_id = get_identifier(tag='id_source',
                           dicom=dicom,
                           template=config['entity'])
```

and the correct value is returned

```
source_id
'PatientID'
```

For a more complicated example, we can see what happens when we give a list of values, as is the case for `custom_fields`:

```
custom_fields = get_identifer('custom_fields',
                               dicom=dicom,
                               template=config['entity'])

custom_fields
[{'key': 'PatientID', 'value': '12SC1'},
 {'key': 'PatientBirthDate', 'value': ''},
 {'key': 'PatientName', 'value': 'CompressedSamples^SC1'},
 {'key': 'ReferringPhysicianName', 'value': '^^^^'}]
```

We are returned a list of dict, each with key/value pairs. We can run this in full, with debug output, for one dicom image, and see first the response in the terminal interface:

```
DEBUG entity id: 12SC1
DEBUG entity source_id: PatientID
DEBUG item id: 1.3.6.1.4.1.5962.1.1.12.1.1.20040826185059.5457
DEBUG entity custom_fields: [{'key': 'PatientID', 'value': '12SC1'}, {'key': 'PatientName', 'value': 'CompressedSamples^SC1'}, {'key': 'ReferringPhysicianName', 'value': '^^^^'}]
DEBUG item source: SOPInstanceUID
DEBUG item custom_fields: [{'key': 'ContentDate', 'value': '19970706'}, {'key': 'ImageComments', 'value': 'Uncompressed'}, {'key': 'InstanceCreationDate', 'value': '20040826'}, {'key': 'InstanceCreationTime', 'value': '185744'}, {'key': 'InstanceCreatorUID', 'value': '1.3.6.1.4.1.5962.3'}, {'key': 'SeriesDate', 'value': '19950705'}, {'key': 'SeriesInstanceUID', 'value': '1.3.6.1.4.1.5962.1.3.12.1.20040826185059.5457'}, {'key': 'SeriesNumber', 'value': '1'}, {'key': 'SOPClassUID', 'value': '1.2.840.10008.5.1.4.1.1.7'}, {'key': 'SOPInstanceUID', 'value': '1.3.6.1.4.1.5962.1.1.12.1.1.20040826185059.5457'}, {'key': 'StudyDate', 'value': '20040826'}, {'key': 'StudyID', 'value': '12SC1'}, {'key': 'StudyInstanceUID', 'value': '1.3.6.1.4.1.5962.1.2.12.20040826185059.5457'}, {'key': 'StudyTime', 'value': '185059'}]
```

and the final data structure produced (note that this example is for one entity that one one item, or dicom image):
```
{
   "12SC1":{
      "identifiers":{
         "custom_fields":[
            {
               "key":"PatientID",
               "value":"12SC1"
            },
            {
               "key":"PatientBirthDate",
               "value":""
            },
            {
               "key":"PatientName",
               "value":"CompressedSamples^SC1"
            },
            {
               "key":"ReferringPhysicianName",
               "value":"^^^^"
            }
         ],
         "id":"12SC1"
      },
      "items":[
         {
            "custom_fields":[
               {
                  "key":"ContentDate",
                  "value":"19970706"
               },
               {
                  "key":"ImageComments",
                  "value":"Uncompressed"
               },
               {
                  "key":"InstanceCreationDate",
                  "value":"20040826"
               },
               {
                  "key":"InstanceCreationTime",
                  "value":"185744"
               },
               {
                  "key":"InstanceCreatorUID",
                  "value":"1.3.6.1.4.1.5962.3"
               },
               {
                  "key":"SeriesDate",
                  "value":"19950705"
               },
               {
                  "key":"SeriesInstanceUID",
                  "value":"1.3.6.1.4.1.5962.1.3.12.1.20040826185059.5457"
               },
               {
                  "key":"SeriesNumber",
                  "value":"1"
               },
               {
                  "key":"SOPClassUID",
                  "value":"1.2.840.10008.5.1.4.1.1.7"
               },
               {
                  "key":"SOPInstanceUID",
                  "value":"1.3.6.1.4.1.5962.1.1.12.1.1.20040826185059.5457"
               },
               {
                  "key":"StudyDate",
                  "value":"20040826"
               },
               {
                  "key":"StudyID",
                  "value":"12SC1"
               },
               {
                  "key":"StudyInstanceUID",
                  "value":"1.3.6.1.4.1.5962.1.2.12.20040826185059.5457"
               },
               {
                  "key":"StudyTime",
                  "value":"185059"
               }
            ],
            "id_source":"SOPInstanceUID"
         }
      ]
   }
}
```

#### Giving Identifiers to API
Our next task is to take the data structure above, amd give it to some API client that can send it to DASHER to return the de-identifiers to replace in the data. First note that the return of the `get_identifiers` function is indexed by the `entity_id`, and this is done in the case that different entities were found in the list of dicom files. For each of these found entities, we want to do one call to the API (note the API or client might support a list, so this is apt to change). For the current single call expectation, here is an example of how we might import the client to make the request:

```
from som.api.identifiers.dicom import get_identifiers
from som.api.identifiers import Client

som_client = Client()

# Here is the function we walked through above, returns a dict
ids = get_identifiers(dicom_files)

deids = []
for entity_id,data in ids.items():
    response = client.deidentify(ids=data)
    deids.append(response)
```

In the above example, we don't specify `save_records=True` or a study parameter, so this would be using a test endpoint and not save data. We save the response (one call per each entity_id to the api endpoint, and note this may change so that `deidentify` can handle the list, either within the function or in the API itself) to a list, and it is this list that we will then use to replace identifiers in the data with the function `replace_identifiers`, also provided in [tasks.py](tasks.py).

#### Replacing Identifiers in Data
We now have generated data structures to describe entities in dicom files, handed those data structures to an API client, and received a list of responses, each associated with one call to the API (one entity/source_id). After this, the application needs to handle the response to de-identify the images, which would be another call to a function provided by the `identifiers.dicom` module. The call would look like this:

```
from som.api.identifiers.dicom import replace_identifiers

updated_files = replace_identifiers(dicom_files=dicom_files,
                                    response=batch_ids.response)        
```

By default, the function overwrites the current files (since they are deleted later). But if you want to change this default behavior, you can ask it to write them instead to a temporary directory:

```
updated_files = replace_identifiers(dicom_files=dicom_files,
                                    response=batch_ids.response)        
                                    overwrite=False)
```

How we know how to deal with the response to properly de-identify the data. A few important points. The response from the function `get_identifiers` is going to return a dictionary, indexed by patient id (or source_id). The reason for this is because the function cannot be sure if a user will provide a list that has more than one source_id represented. The response will generally look like this:

```
{
 '12SC1': {'identifiers': {...}},
 '12SC2': {'identifiers': {...}}
}
```

**Note** the function above may change, I would prefer to pass around lists of identifiers, and am just figuring out what the API can handle, versus the client and these functions. For now I'll write what is implemented.

In the example above, a set of dicom files was provided that had two source ids, `12SC1` and `12SC2`. This is why when we do calls to the `deidentify` function, since we want to provide a datastructure with 


`deidentify` will return


#### Responses
A Response is going to need to know how to receive a respones from the identifiers API, and substitute values back into the data to properly de-identify it. We might also want to add fields to indicate that it's been de-identified. It follows then, that the `response` section of the [config.json](config.json) has settings for `actions` and `additions`:

```
{
  "response": {
 
               "actions":{}
               "additions":{}

    }

}
```

In the [tasks.py](tasks.py) file, the function called `replace_identifiers` should know how to take a valid response from the API, the dicom image it is matched to, and a [config.json](config.json) file, and perform this task.

##### Actions
Actions are a list of header values, and for each, how to deal with the header in the data. Each entry in actions includes a dictionary, each is a simple key (the field name) and value (the action). Let's look at an example.

```

   "actions": {

     "*":"blank",
     "PatientID":"coded",
     "SOPInstanceUID":"coded"

   }

```

The first `*` is a catch all for the action to take for any that we didn't specify. In this case, we blank them, which is a good conservative approach to take. The valid options for `action` (the value) are:

 - coded: use the response from the API to code the item. If no response is provided, blank it.
 - blanked: blank the response (meaning replace with an empty string)
 - original: do not touch the original identifier.
 - removed: completely remove the field and value from the data/header

Valid actions names are provided in [standards.py](standards.py). If the user has not specified a default with the `*` operator, then the default taken is the most conservative, blanked. If the user specifies an invalid action, `blanked` is also used. In most cases, fields that are provided to the API as `custom_fields` are likely PHI and should be blanked, and only `source_id` and `id` should be coded. It is generally best to not remove fields, but to blank them instead, and care should be kept that original values are only kept if they are absolutely not PHI.


##### Additions
If the config has specified additions, each call to `replace_identifiers` will add the set provided to all dicom_files given to the function call. For example, if I have a set of `dicom_files` for a (patient id) indexed list from `get_identifiers` I might do the following:

```
DEBUG PatientIdentityRemoved will be added as Yes to all datasets.
```
