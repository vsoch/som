# swagger_client.DevelopersApi

All URIs are relative to *https://virtserver.swaggerhub.com/susanweber/UID/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**uid**](DevelopersApi.md#uid) | **POST** /v1/api/suid/:study | Accepts a list of identified items, returns a list of study specific identifiers


# **uid**
> UidEntityList uid(token, identifiers=identifiers)

Accepts a list of identified items, returns a list of study specific identifiers

At least one of person or items must be present in each Identifier object 

### Example 
```python
from __future__ import print_statement
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DevelopersApi()
token = 'token_example' # str | required authentication token
identifiers = swagger_client.EntityList() # EntityList | Array of Entity (optional)

try: 
    # Accepts a list of identified items, returns a list of study specific identifiers
    api_response = api_instance.uid(token, identifiers=identifiers)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DevelopersApi->uid: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| required authentication token | 
 **identifiers** | [**EntityList**](EntityList.md)| Array of Entity | [optional] 

### Return type

[**UidEntityList**](UidEntityList.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

