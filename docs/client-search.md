# Search and Summarize Images and Text

<script src="assets/js/asciinema-player.js"></script>
<link rel="stylesheet" href="assets/css/asciinema-player.css"/>

<asciinema-player src="assets/asciicast/client-search.json" poster="data:text/plain,Intro to SOM Search" title="How to search the SOM DataStore" author="vsochat@stanford.edu" cols="124" rows="24" speed="2.0" theme="asciinema"></asciinema-player>


After installing the som tools:

```
git clone https://www.github.com/vsoch/som
cd som
python setup.py install
```

You can type the command `som` to see it's usage:

```
usage: som [-h] [--version] [--debug] {list,get} ...

Stanford Open Modules for Python [SOM]

optional arguments:
  -h, --help  show this help message and exit
  --version   show software version
  --debug     use verbose logging to debug.

actions:
  actions for som tools

  {list,get}  google storage and datastore
    list      list collections, entities, images.
    get       download data from storge and datastore
```

Make sure your project credentials are exported:

```
GOOGLE_APPLICATION_CREDENTIALS=/top/secret/pizza.json
export GOOGLE_APPLICATION_CREDENTIALS
```

GOOGLE_APPLICATION_CREDENTIALS=/home/vanessa/.vanessasaur/som-irlearning.json 


Let's list to see a summary for a project:

```
som list --project som-irlearning

Collections: 1
Images: 933
Entity: 233
```

Now let's look just at Collection entries

```
som list --project som-irlearning --collections

Collection: IRB33192
updated 2017-08-28 03:28:45.640733+00:00
created 2017-08-22 03:00:53.982025+00:00
uid IRB33192

Found 1 collections

```

Entities?

```
som list --project som-irlearning --entity

...

Entity: IR664a78
UPLOAD_AGENT STARR:SENDITClient
created 2017-08-27 20:20:11.107150+00:00
id IR664a78
uid IR664a78
updated 2017-08-27 20:20:11.312405+00:00
PatientSex F

Entity: IR664a82
uid IR664a82
UPLOAD_AGENT STARR:SENDITClient
PatientAge 067Y
PatientSex F
updated 2017-08-27 20:29:05.324285+00:00
created 2017-08-27 20:29:05.212657+00:00
id IR664a82

Found 233 entities
```

And images (each is a compressed set, and they have quite a lot of metadata):

```
som list --project som-irlearning --images

Image: Collection/IRB33192/Entity/IR664a82/IR664a82_20070117_IR664a84.tar.gz
InstitutionName Stanford Med. Center
DataCollectionDiameter 500.000000
ConversionType WSD
BitsAllocated 16
uid Collection/IRB33192/Entity/IR664a82/IR664a82_20070117_IR664a84.tar.gz
PositionReferenceIndicator SN
Modality CT
StationName SCT1_OC0
SoftwareVersions LightSpeedApps308I.2_H3.1M5
ContrastBolusRoute IV
PatientSex F
2FIR664a82_20070117_IR664a84.tar.gz?generation=1503865797682327&alt=media
ContrastBolusAgent OMNI350
IssuerOfPatientID STARR. In an effort to remove PHI all dates are offset from their original values.
TableHeight 105.099998
PhotometricInterpretation MONOCHROME2
RequestingService EMERGENCY DEPARTMENT *
KVP 120
PatientIdentityRemoved Yes
PixelPaddingValue -2000
HighBit 15

...

StudyDate 2007-01-17T00:00:00-0800
RescaleIntercept -1024

Found 933 images
```

Filter to a subset?

```
som list --project som-irlearning --images --filter Modality,=,CT
```
