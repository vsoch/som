# SOM API

This is a python wrapper for the School of Medicine (SOM) API. Content in the following files includes:

## Main Modules
- [auth.py](auth.py): contains a simple function to authenticate a person with the API. This might turn into a client object that can carry around an authentication to perform multiple calls, but right now is a simple token header returned.
- [base.py](base.py): contains the default (current) endpoint and version of the API, along with core functions that are used across modules (eg, `radiology` has a particular endpoint to send images with an identifier, and these extend/use base functions for creating a person, item, etc.
- [validators](validators): contains functions (for [requests](validators/requests.py) and [responses](validators/responses.py), respectively) that serve only to validate json data structures that are intended to go into POSTs. If a data structure is valid, True is returned. If not, False is returned, and the debugger prints why the structure is not valid for the user.
- [standards.py](standards.py): Within validation, there are certain fields that must match a particular pattern, be required, etc. This file holds lists/sets of items that are to be used as defaults for some of these items. The user has the option to define these lists with the validator functions, and if not defined, the defaults in this file are used. For example.
- [utils.py](utils.py): contains base http utility functions to perform `GET`, `POST`, and `PUT`, and whatever other functions we need.


## Domain Modules
- [radiology.py](radiology.py): Includes functions to post messages that have a person identifier and sets of items, in this case, a list of images to be de-identified.
