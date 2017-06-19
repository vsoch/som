# Development
This section is intended for those interested in how the identifiers module works, in the case you want to extend or change it, or make a different module for another endpoint. If  we look at the entire application, the api modules are organized as follows:


```
som/api
├── base
├── google
├── __init__py
└── identifiers
```

What is in each folder?

 - **base** is base authentication and client classes for the School of Medicine (dasher) API. A new endpoint, for example, would extend the base client here.
 - **__init__.py**: is hiding an even more general API client to get, post, etc, but without the modules specific to DASHER for authentication. If you wanted to add an API module for the package not related to DASHER, you could start here.
 - **google**: is the folder that has modules for google storge, datastore, and a (beta DLP) that we didn't wind up doing anything with.
 - **identifiers** is the API that handles sending and retrieving identifiers via DASHER, the topic of this discussion. 

Let's look more closely at identifiers. Identifiers is structured like this:

```
som/api/identifiers
├── client.py
├── data
├── dicom
├── standards.py
├── utils.py
└── validators
```

The main client (an instance of the class defined in [base](../som/api/base) mentioned above has functions to deidentify, and the following:

 - **client.py**: is the core client to communicate with the API, which extends the `SomApiConnection` under `base`. The client can take a specific study or it not provided, will default to `test`.
 - **data**: is example data for the user to see what a request should look like, and what is used in the [walkthrough](identifiers.md).
 - **standards.py** Within validation, there are certain fields that must match a particular pattern, be required, etc. This file holds lists/sets of items that are to be used as defaults for some of these items. The user has the option to define these lists with the validator functions, and if not defined, the defaults in this file are used. This file also contains valid study names, along with the url of the swagger specification for the API.
 - **utils.py**: speaks for itself.
 - **validators**: contains functions [requests](../som/api/identifiers/validators/requests.py) and [responses](../som/api/identifiers/validators/responses.py) that serve only to validate json data structures that are sent and received. It's better to catch the error before you trigger it.

The dicom folder is a module for defining settings for preparing the request to the API from extracted identifier for the data, discussed next.


## Dicom
The [dicom](../som/api/identifiers/dicom) module contains functionality for working with dicom. Before we talk about this module, it's important to distinguish two things that are working together, but very different:

 - deidentification of the data, meaning getting identifiers, and putting something back
 - communicating with the DASHER API to send extracted identifiers for secure storage, and then getting alias identifiers back

This application specializes in the second, and for the first (needed) functionality, we use a module called [deid](https://www.github.com/pydicom/deid). We do this so that, if someone wanted to de-identify outside of the API, that would be possible. 

### Step 1: The De-id Recipe
We can tell deid how to repace identifiers by defining a [recipe](../som/api/identifiers/dicom/deid.som). For more details on how deid works, see [its docs](https://pydicom.github.io/deid). Our default recipe that we enforce for the identifiers endpoint will use the default to blank all fields (this is a default of deid) and then replace entity and item identifiers with those returned from DASHER. The recipe looks like this:

```
FORMAT dicom

%header

REPLACE PatientID var:entity_id
REPLACE SOPInstanceUID var:item_id
ADD PatientIdentityRemoved "Yes"
REPLACE PatientBirthDate var:entity_timestamp
REPLACE InstanceCreationDate var:item_timestamp
REPLACE InstanceCreationTime var:item_timestamp
```

### Step 2: Extract identifiers
We don't need to use the recipe to extract identifiers, as the default deid will give us everything back that it finds (aside from pixel data). However, after extraction, we need to know which of those identifiers we want to send to DASHER as `custom_fields` for saving, and which identifiers in the data map to the variables of `source_id`, etc, that the API expects to get. To do this, we define a dicom [settings](../som/api/identifiers/dicom/settings.py) to enforce the fields that we want to send to the API to keep securely. For example, here is the specification for an entity:


```

entity = {'id_source': 'PatientID',
          'id_timestamp': {"date":"PatientBirthDate"},
          'custom_fields':[ "AccessionNumber",
                            "OtherPatientIDs",
                            "OtherPatientNames",
                            "OtherPatientIDsSequence",
                            "PatientAddress",
                            "PatientBirthDate",
                            "PatientBirthName",
                            "PatientID",
                            "PatientMotherBirthName",
                            "PatientName",
                            "PatientTelephoneNumbers",
                            "ReferringPhysicianName"
                          ]
         }

```

And logically, it follows that if you want or need to change any of the data going to DASHER, this would be the file to change.


### Step 3: Send to Dasher
As we saw in the [example provided](identifiers.md), the last step is to send the prepared request to DASHER.

Generally, as a developer, you can use this dicom folder as a template for a different data type, and write the corresponding functions for your datatype. Please [post an issue](https://www.github.com/vsoch/som/issues) if you have questionsor need help with this task.

Finally, you might be wondering "what happens between getting identifiers from the data (with [deid](https://pydicom.github.io/deid)) and sending a request to the API? We need to do stuff like calculate timestamps, and generate the datastructure. This module can only validate it once that is done. The answer is that more specific logic for creating the variables is implemented by the application using the API, for example, [sendit](https://pydicom.github.io/sendit). 
