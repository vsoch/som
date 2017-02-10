# UidEntity

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | this is the external identifier for which a unique study id should be returned | 
**id_source** | **str** | this scopes the identifier, since different source systems may wind up inadvertently using the same identifier | 
**suid** | **str** | this is the Stanford UID or &#39;suid&#39; generated for the supplied id and id_source pair in the context of the current study | 
**jittered_timestamp** | **str** | if the optional associated timestamp was supplied in the input message, this will be returned, suitably date-shifted from the original | [optional] 
**custom_fields** | [**list[CustomField]**](CustomField.md) | QUESTION Should this be returned in the response? | [optional] 
**items** | [**list[UidChildEntity]**](UidChildEntity.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


