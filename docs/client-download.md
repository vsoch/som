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

usage: som get [-h] [--outfolder OUTFOLDER] --project PROJECT --suid SUID
               [--query-images] --bucket BUCKET --collection COLLECTION

optional arguments:
  -h, --help            show this help message and exit
  --outfolder OUTFOLDER
                        full path to folder for output, stays in tmp (or pwd)
                        if not specified
  --project PROJECT     name of Google Cloud project (eg, irlhs-learning)
  --suid SUID           An suid associated with an entity to find images
                        (default) or query single images (set flag --query-
                        images for the study. Typically begins with IRXXXX
  --query-images        use verbose logging to debug.
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
 - suid: This is a stanford unique id associated with a patient (de-identified). The default of the client is to query across all studies for a single Patient ID, and in this case, you would set the suid to be on the level of the patient. If you want to query across the compressed images, then set the suid to be a study identifier, and also set the flag `--query-images`. 
 - bucket: the Google Cloud Storage bucket. This also needs to be given to you, if you don't know.
 - collection: the collection is typically named by your IRB. This should also be given to you.

## API Call

An example API Call might look like the following:


```
som get --outfolder /tmp --project som-irlearning --suid IR661f32 --bucket irlhs-dicom --collection IRB33192
Collecting available images...
Found 2 images for suid IR661f32 in collection IRB33192
DEBUG Saving images and metadata...
Progress |===================================| 100.0% 
```

Yeah it's a lot of parameters. We try to make this really hard on your memory centers :)
