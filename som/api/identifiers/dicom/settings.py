'''
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
'''


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


item = {'id_source': 'SOPInstanceUID',
        'id_timestamp': {"date":"InstanceCreationDate",
                         "time":"InstanceCreationTime"},
        'custom_fields': ["AcquisitionDate",
                          "ContentDate",
                          "CurrentRequestedProcedureEvidenceSequence",
                          "EquipmentModality",
                          "FillerOrderNumberImagingServiceRequest",
                          "ImageComments",
                          "InstanceCreationDate",
                          "InstanceCreationTime",
                          "InstanceCreatorUID",
                          "MediaStorageSOPInstanceUID",
                          "MedicalRecordLocator",
                          "Modality",
                          "ModalityLUTSequence",
                          "ModalityLUTType",
                          "PerformedProcedureCodeSequence",
                          "ProcedureVersion",
                          "ProcedureCreationDate",
                          "ProcedureExpirationDate",
                          "ProcedureLastModifiedDate",
                          "PerformedProcedureTypeDescription",
                          "PerformedProcedureStepID",
                          "ProcedureStepProgressDescription",               
                          "ProcedureStepCommunicationsURISequence",
                          "PerformedProcedureStepEndDate",
                          "PerformedProcedureStepStatus",
                          "PerformedProcedureStepDescription",
                          "RequestAttributesSequence",
                          "ReasonForRequestedProcedureCodeSequence",
                          "ScanProcedure",
                          "SeriesDate",
                          "SeriesInstanceUID",
                          "SeriesNumber",
                          "SOPClassUID",
                          "SOPInstanceUID",
                          "SpecimenAccessionNumber",
                          "StudyDate",
                          "StudyID",
                          "StudyInstanceUID",
                          "StudyTime"]



       }
