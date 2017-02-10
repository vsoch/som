# ChildEntity

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | this is the external identifier for which a unique study id should be returned | 
**id_source** | **str** | this scopes the identifier, since different source systems may wind up inadvertently using the same identifier | 
**id_timestamp** | **str** | an optional associated timestamp which if supplied will be returned offset by a random whole number in the discontinous range [-33,-3] or [3,33] associated with the study identifier i.e. \&quot;jittered\&quot; | [optional] 
**custom_fields** | [**list[CustomField]**](CustomField.md) | an optional set of information associated with the identifier | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


