#!/bin/env python

# This is an example script to upload data (images, text, metadata) to
# google cloud storage and datastore. We use the wordfish standard,
# assuming the data has been de-identified. The first step 
# below we structure our dataset. This also validates that it's
# formatted correctly. In the second step, we use the radiology
# client to upload the structures to storage and datastore.


from som.api.google.dlp.client import DLPApiConnection
import pandas

dlp = DLPApiConnection()

def run_cleaning_example(texts):
    df = pandas.DataFrame()
    df['cleaned'] = dlp.remove_phi(texts=texts)
    df['original'] = texts
    return df


# Knees
knee_reports = pandas.read_csv('Knee_UniqueID_ReportOnly.csv') 
knee_reports.columns = ['exam', 'modality', 'unique_id', 'report_text']
texts = knee_reports.report_text.tolist()
df = run_cleaning_example(texts)
df.to_csv('knees_scrubbed.tsv',sep="\t")


# Shoulders
shoulder_reports = pandas.read_csv('Shoulder_UniqueID_ReportOnly.csv') 
shoulder_reports.columns = ['exam', 'modality', 'unique_id', 'report_text']
texts = shoulder_reports.report_text.tolist()

df = pandas.DataFrame()
df['cleaned'] = dlp.remove_phi(texts=texts)
df['original'] = texts
df.to_csv('shoulders_scrubbed.tsv',sep="\t")
