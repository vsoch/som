'''
dicom.py: functions to extract identifiers from dicom images

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


from som.logger import bot
from pydicom import read_file
from .defaults import GE_PACS
from pydicom.errors import InvalidDicomError


# Default dicom header fields associated with each of Entity
# (the primary in the list of identifiers) and the associated
# Items

class Entity:
    custom_fields = ["PatientID"
                     "OtherPatientIDs", 
                     "OtherPatientNames", 
                     "OtherPatientIDsSequence",
                     "PatientAddress",
                     "PatientBirthDate",
                     "PatientBirthName",
                     "PatientMotherBirthName",
                     "PatientName", 
                     "PatientTelephoneNumbers",
                     "ReferringPhysicianName"]

    # IMPORTANT: need to verify this
    id = "AccessionNumber"
    defaults = {"id_source": "Stanford MRN",
                "id_timestamp":{}}


class Item:
    id = "InstanceNumber" # not unique
    id_source = "InstanceCreatorUID"
    custom_fields = ["ContentDate",
                     "ImageComments",
                     "InstanceCreationDate",
                     "InstanceCreationTime",
                     "InstanceCreatorUID",
                     "MedicalRecordLocator",
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


# Return a list of identifiers (each a separate request to the identifiers API)

def get_identifiers(dicom_files,force=True):
    '''extract and validate identifiers from a dicom image that conform
    to the expected request to the identifiers api.
    :param dicom_files: the dicom file(s) to extract from
    :param force: force reading the file (default True)
    '''
    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]

    ids = dict() # identifiers
    entity = Entity()
    template = Item()

    for dicom_file in dicom_files:
        dicom = read_file(dcm.image.path,force=True)
        entity_id = dicom.get(entity.id, None)
        item_id = dicom.get(template.id,None)

        # Skip images without patient id or item id
        if entity_id is not None and item_id is not None:
           if entity_id not in ids:
               ids[entity_id] = {'identifiers': entity.defaults } 
               ids[entity_id]['identifiers']['id'] = patient_id,
               ids[entity_id]['identifiers']["custom_fields"] = {} 
               ids[entity_id]['items'] = []

            # Add each custom field, if present
            for cf in entity.custom_fields:
                value =  dicom.get(cf,None)
                if value not in [None,'',' ']:
                    ids[patient_id]['identifiers']['custom_fields'][cf] = value

            item = {'custom_fields':{}}
            item['id_source'] = dicom.get(entity.id_source,GE_PACS)

            for cf in template.custom_fields:
                value =  dicom.get(cf,None)
                if value not in [None,'',' ']:
                    item[['custom_fields'][cf] = value
            ids[entity_id]['items'].append(item) 

        else:
            bot.warning("Skipping %s due to empty entity (%s) or item (%s) id" %(dicom_file,entity_id,item_id))
    return ids
