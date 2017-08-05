"""
settings.py: fields to send to the som API, distinct from the de-identification

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# This is associated with a patient

entity = {

   "id_source":{
      "field":"PatientID",
      "name":"Stanford MRN"
   },
   "id_timestamp":{
      "date": [
         "PatientBirthDate"
      ]
   },
   "custom_fields":[
      "AccessionNumber",
      "AffectedSOPClassUID",
      "AffectedSOPInstanceUID",
      "AssertionUID",
      "CodingSchemeUID",
      "ConcatenationUID",
      "ContextGroupExtensionCreatorUID",
      "ContextUID",
      "CreatorVersionUID",
      "DeviceUID",
      "DigitalSignatureUID",
      "DimensionOrganizationUID",
      "DoseReferenceUID",
      "EncryptedContentTransferSyntaxUID",
      "FiducialUID",
      "FillerOrderNumberImagingServiceRequest",
      "FrameOfReferenceUID",
      "ImplementationClassUID",
      "InstanceCreatorUID",
      "IrradiationEventUID",
      "LargePaletteColorLookupTableUID",
      "MACCalculationTransferSyntaxUID",
      "MappingResourceUID",
      "MediaStorageSOPClassUID",
      "MediaStorageSOPInstanceUID",
      "MultiFrameSourceSOPInstanceUID",
      "ObservationUID",
      "OriginalSpecializedSOPClassUID",
      "OtherPatientIDs",
      "OtherPatientIDsSequence",
      "OtherPatientNames",
      "PaletteColorLookupTableUID",
      "PatientAddress",
      "PatientBirthDate",
      "PatientBirthName",
      "PatientID",
      "PatientMotherBirthName",
      "PatientName",
      "PatientTelephoneNumbers",
      "PresentationDisplayCollectionUID",
      "PresentationSequenceCollectionUID",
      "PrivateInformationCreatorUID",
      "PrivateRecordUID",
      "RadiopharmaceuticalAdministrationEventUID",
      "ReasonForStudyReferencedGeneralPurposeScheduledProcedureStepTransactionUID",
      "ReferencedAssertionUID",
      "ReferencedColorPaletteInstanceUID",
      "ReferencedDoseReferenceUID",
      "ReferencedFrameOfReferenceUID",
      "ReferencedSOPClassUID",
      "ReferencedSOPInstanceUID",
      "RelatedFrameOfReferenceUID",
      "RelatedGeneralSOPClassUID",
      "RequestedSOPClassUID",
      "RequestedSOPInstanceUID",
      "RetrieveLocationUID",
      "SOPClassUID",
      "SOPInstanceUID",
      "SeriesInstanceUID",
      "SourceFrameOfReferenceUID",
      "SpecimenUID",
      "StorageMediaFileSetUID",
      "StudyInstanceUID",
      "StudyID",
      "SynchronizationFrameOfReferenceUID",
      "TableFrameOfReferenceUID",
      "TargetFrameOfReferenceUID",
      "TargetUID",
      "TemplateExtensionCreatorUID",
      "TemplateExtensionOrganizationUID",
      "TrackingUID",
      "TransactionUID",
      "TransferSyntaxUID",
      "UID",
      "VolumeFrameOfReferenceUID",
      "VolumetricPresentationInputSetUID"
   ]
}

# This is associated with an entire study

item = {

   "id_source":{
      "field":"AccessionNumber",
      "name":"DCM Accession #"
   },
   "id_timestamp":{
      "date":[
         "StudyDate",
         "SeriesDate",
         "ContentDate",
         "AcquisitionDate"
      ]
   }
}
