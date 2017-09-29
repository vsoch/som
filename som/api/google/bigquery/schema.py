'''
google/modals.py: models for datastore

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

from google.cloud import bigquery


dicom_schema = (
    bigquery.SchemaField('entity_id', 'STRING'),
    bigquery.SchemaField('item_id', 'STRING'),
    bigquery.SchemaField('AccessionNumber', 'STRING'),
    bigquery.SchemaField('PatientID', 'STRING'),
    bigquery.SchemaField('PatientSex', 'STRING'),
    bigquery.SchemaField('PatientAge', 'STRING'),

    bigquery.SchemaField('width', 'INTEGER'),
    bigquery.SchemaField('height', 'INTEGER'),
    bigquery.SchemaField('ImageType', 'STRING'),
    bigquery.SchemaField('Modality', 'STRING'),

    bigquery.SchemaField('StudyDescription', 'STRING'),
    bigquery.SchemaField('BodyPartExamined', 'STRING')
)

