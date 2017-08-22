# Download Images and Metadata

After installing the som tools:

```
pip install som
```

You can type the command `som` to see it's usage:

```
usage: som [-h] [--version] [--debug] {get} ...

Stanford Open Modules for Python [SOM]

optional arguments:
  -h, --help  show this help message and exit
  --version   show software version
  --debug     use verbose logging to debug.

actions:
  actions for som tools

  {get}       google storage and datastore
    get       download data from storge and datastore

```

Right now the only thing this client does is download data, meaning images and metadata:

 - metadata is from Google DataStore
 - images are from Google Storage

Specifically, we query datastore to get some subset, and then use the download links from datastore to retrieve them in Storage. Let's take a look more closely at the get command:

```
som get --help

usage: som get [-h] [--outfolder OUTFOLDER] --project PROJECT --study STUDY
               --bucket BUCKET --collection COLLECTION

optional arguments:
  -h, --help            show this help message and exit
  --outfolder OUTFOLDER
                        full path to folder for output, stays in tmp (or pwd)
                        if not specified
  --project PROJECT     name of Google Cloud project (eg, irlhs-learning)
  --study STUDY         Identifier for the study. Typically begins with IRXXXX
  --bucket BUCKET       Name of the storage bucket. Eg (irlhs-dicom)
  --collection COLLECTION
                        name of collection (eg, IRB33192)
```

## Credentials
Before this will work for you, you need to be given a credentials file, and you need to export the path to this credentials file in your environment. For example, let's say I saved my top secret credentials in the file `/home/vanessa/.secrets/hufflepuff.json`. This could be in my `$HOME/.bashrc` or `$HOME/.profile`:

```
GOOGLE_APPLICATION_CREDENTIALS="/home/vanessa/.secrets/hufflepuff.json"
export GOOGLE_APPLICATION_CREDENTIALS 
```

This is important so your credentials are discovered automatically. If you don't do this, you will get permissions errors (in the family of 400).

## Parameters
If you notice from the help above, we need to have several parameters.

 - outfolder: should be an output folder for your study folder to be generated, and images and associated metadata saved.
 - project: should be the name of the Google Cloud Project. Likely this needs to be given to you.
 - study: the name of the study, which is typically an SUID generated for some AccessionNumber/PatientID combination
 - bucket: the Google Cloud Storage bucket. This also needs to be given to you, if you don't know.
 - collection: the collection is typically named by your IRB. This should also be given to you.

## API Call

An example API Call might look like the following:


```
som get --outfolder /tmp --project som-learning --study IR666666 --bucket som-bucket --collection IRB33333
```

Yeah it's a lot of parameters. We try to make this really hard on your memory centers :)
