# Stanford Open Modules
The Stanford Open modules for Python implement several modules for moving and structuring data, and communicating with different API endpoints. This documentation base will go over some basic examples for usage.

## Clients
If you want to use the client, the software provides a command line utility, `som`, to do so.

 - [Download Images](client-download.md): Here is a walkthrough to download images and associated metadata from Google Storage and Datastore.


## Data Structure

  - [wordfish-standard](): The core of many of these modules is the wordfish standard, which is a simple file organization hierarchy for general groups of things called Collections, each of which has an Entity, and some number of Images and Text. For details on the organization, for now go to the [example datasets](https://github.com/vsoch/wordfish-standard). The nice thing about this simple approach is that these general categories map nicely onto many different domains. For example, this would work on a file system, or in Google Storage, or modeled in a relational database:

```
Collection / [ collection name ]/ Entity / [ entity name ] / Images / [ image name ]
Collection / [ collection name ]/ Entity / [ entity name ] / Text / [ image name ]

# Manscripts
Collection / Science / Entity / PMID1234 / Images / science-image.gif
Collection / Science / Entity / PMID1234 / Text / article.txt

# Clinical
Collection / Study / Entity / SUID123 / Images / suid123-1.dcm
Collection / Study / Entity / SUID123 / Text / radiology-notes.txt
```


## Application Program Interaces

 - [google](google.md): A client is provided to move Collections defined in the Wordfish Standard onto Google Storage, and metadata into DataStore. The two are linked, so that you can query DataStore to find what you are looking for in Storage.
 - [identifiers](identifiers.md): A client is provided to communicate with the identifiers API (DASHER) at the Stanford school of medicine to get identifiers for images.
 - [developers](identifiers-developers.md): A brief review of how identifiers works, to be better parsed out into different documentation bases if/when the application expands.
