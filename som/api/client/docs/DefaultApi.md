# swagger_client.DefaultApi

All URIs are relative to *https://virtserver.swaggerhub.com/susanweber/UID/1.0.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**mrn**](DefaultApi.md#mrn) | **POST** /v1/api/mrn/:mrn | Accepts a list of Stanford MRNs with optional name and date of birth, returns a list of invalid MRNs or empty list if no problems found


# **mrn**
> ValidMrnList mrn(token, mrns=mrns)

Accepts a list of Stanford MRNs with optional name and date of birth, returns a list of invalid MRNs or empty list if no problems found

### Example 
```python
from __future__ import print_statement
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
token = 'token_example' # str | required authentication token
mrns = swagger_client.StanfordMrnList() # StanfordMrnList | Array of StanfordMrn (optional)

try: 
    # Accepts a list of Stanford MRNs with optional name and date of birth, returns a list of invalid MRNs or empty list if no problems found
    api_response = api_instance.mrn(token, mrns=mrns)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->mrn: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| required authentication token | 
 **mrns** | [**StanfordMrnList**](StanfordMrnList.md)| Array of StanfordMrn | [optional] 

### Return type

[**ValidMrnList**](ValidMrnList.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

