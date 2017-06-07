#!/usr/bin/env python

'''

structures.py: generate json (dict) structures to represent folders, etc.

'''

from som.logger import bot
import tempfile
import shutil
import os
import re
import json
import sys

from som.utils import (
    untar_dir,
    unzip_dir,
    read_json
)

from validator import (
    Required, 
    Not, 
    Truthy, 
    Blank, 
    Range, 
    Equals, 
    In, 
    validate
)


def structure_dataset(dataset,testing_base=None,clean_up=True):
    '''structure_dataset is a general function to take a compressed object 
    (zip or .targz) or folder and run the correct functions to return a json
    datastructure, depending on the input types
    :param dataset: the full path to the dataset
    :param testing_base: the testing_base directory
    :param clean_up: whether to clean up the directory upon finish
    '''
    if os.path.isdir(dataset):
        structure = structure_folder(folder=dataset)
    elif re.search("[.]zip$|[.]tar[.]gz$",dataset):
        structure = structure_compressed(compressed_file=dataset,
                                         testing_base=testing_base,
                                         clean_up=clean_up)
    return structure


def structure_metadata(full_path,metadata_type=None):
    '''structure_metadata checks to see if a name (either a collection
    name, folder for an image or text) has associated metadata, indicated by
    a file of the same name (ending with json) in the parent directory of the
    named file. If no matching files are found, None is returned, and the user
    is alerted. If a matching file is found, the file is read and returned if 
    it's valid json.
    :param full_path: full path to a file or folder
    :param metadata_type: either one of collection, image, or text. Default collection
    '''
    if metadata_type == None:
        metadata_type = "collection"

    parent_dir = os.path.dirname(full_path)
    base_name = os.path.basename(full_path)
    metadata = "%s/%s.json" %(parent_dir,base_name)

    if os.path.exists(metadata):
        bot.debug('found %s metadata: %s' %(metadata_type, base_name))
        try:
            return read_json(metadata)
        except:
            bot.error('%s %s has invalid json metadata %s' %(metadata_type, base_name, metadata))
            return False
 
    else:
        bot.info('%s %s does not have metadata file %s.json' %(metadata_type, base_name, base_name))
        return None


def structure_compressed(compressed_file,testing_base=None,clean_up=False):
    '''structure_compressed will first decompress a file to a temporary location,
    and then return the file structure in the WordFish standard. 
    :param compressed_file: the file to first extract.
    :param testing_base: If not given, a temporary location will be created. Otherwise,
    a folder will be made in testing_base.
    :param clean_up: clean up (remove) extracted files/folders after test. Default False,
    so the user can access the extracted files.
    '''
    if testing_base == None:
        testing_base = tempfile.mkdtemp()
 
    dest_dir = tempfile.mkdtemp(prefix="%s/" %testing_base)
    if compressed_file.endswith('.tar.gz'):
        test_folder = untar_dir(compressed_file,dest_dir)
 
    elif compressed_file.endswith('.zip'):
        test_folder = unzip_dir(compressed_file,dest_dir)

    else:
        bot.error("Invalid compressed file type: %s, exiting." %compressed_file)
        sys.exit(1)

    # Each object in the folder (a collection)
    collection_paths = os.listdir(test_folder)
    bot.info("collections found: %s" %len(collection_paths))

    # We will return a list of structures, only of valid
    collections = []

    for col in collection_paths:
        collection_path = "%s/%s" %(test_folder,col)
        collection = structure_folder(collection_path)
        collections.append(collection)           

    if clean_up == True:
        shutil.rmtree(dest_dir)
    return collections


def structure_folder(folder,relative_path=False):
    '''structure_folder will return a json data structure to describe a collection folder.
    The collection is named according to the input data file, and so if additional metadata
    is to be added (a unique id, name, etc.) it should be done by the calling function using
    the name as a lookup.
    :param folder: the folder to generate a structure for
    :param relative_path: if True, will return relative paths (for web server)
    :returns collection: a dictionary of entity and other objects. 

    A collection is a dictionary with the following:

    { "collection":

      {
         "name": "collection1",
         "metadata" ... ,
         "entities": [ ... ]},
      }
 
    }

    A collection should be put into a collections data structure like:


     { "collections":
         
        [ ... ]

     }

    '''    

    collection = {'name': folder }
    full_path = os.path.abspath(folder)
    if relative_path == True:
        full_path = os.path.relpath(folder, os.getcwd())

    # Add any collection metadata
    metadata = structure_metadata(full_path)
    if metadata != None:
        collection['metadata'] = metadata

    # validate images, text, and metadata of the entities
    entities = structure_entities(full_path)
    if entities == None:
        bot.info("no entities found for collection %s." %(folder))              
    else:
        bot.info("adding %s valid entities to collection %s." %(len(entities),folder))              
        collection['entities'] = entities

    return {"collection" : collection}


def structure_entities(full_path):
    '''structure_entities will return a data structure with a list of
    images and text for each entity found. 
    :param full_path: the full path to the collection folder with entities

    An entity should look like the following:    
        { "entity": {
         
            "id": "12345-6",
            "images": [ ... ],
            "text": [ ... ] 
          }

        },
    '''
    entities = []
    contenders = os.listdir(full_path)
    bot.info("Found %s entity folders in collection." %len(contenders))
    if len(contenders) == 0:
        return None
     
    for contender in contenders:
        entity_path = "%s/%s" %(full_path,contender)
        entity = {'id':entity_path}

        # Does the entity have metadata?
        metadata = structure_metadata(entity_path,"entity")
        if metadata != None:
            entity['metadata'] = metadata

        entity_texts = structure_texts(entity_path)
        entity_images = structure_images(entity_path)

        # If images and text are empty for a collection, invalid
        if entity_texts == None and entity_images == None:
            bot.error("found invalid entity: does not have images or text.")
            continue
    
        # if either text or images are not valid, entities considered invalid
        if entity_texts != None:
            entity['texts'] = entity_texts
        if entity_images != None:
            entity['images'] = entity_images    
        entities.append({"entity":entity})

    return entities


def structure_texts(entity_path,acceptable_types=None):
    '''structure_texts will check an entity directory
    for a text folder. If it exists, each subfolder will return a list of
    texts and metadata
    :param entity_path the path to the top level (entity) folder
    :param acceptable_types: the valid extensions to allow
    '''    
    if acceptable_types == None:
        acceptable_types = ['txt']

    texts = structure_template(entity_path=entity_path, 
                               template_type="text",
                               acceptable_types=acceptable_types)
    return texts


def structure_images(entity_path, acceptable_types=None):
    '''structure_images will check an entity directory
    for an images folder. If it exists, each subfolder will be searched
    for images and corresponding metadata
    :param entity_path the path to the top level (entity) folder
    :param acceptable_types: the valid extensions to allow
    '''    
    if acceptable_types == None:
        acceptable_types = ['dcm','png','jpg','jpeg','nii','nii.gz']

    images = structure_template(entity_path=entity_path, 
                                template_type="images",
                                acceptable_types=acceptable_types)
    return images


def structure_template(entity_path, template_type, acceptable_types):
    '''structure_template will check an entity directory
    for an folder of a particular type, for files and metadata that
    meet a particular criteria. If needed, additional parsing
    functions can be passed to this function. 
    :param entity_path the path to the top level (entity) folder
    :param template_type: should be one of images or text
    :param acceptable_types: the valid extensions to allow
    '''
    template_path = "%s/%s" %(entity_path,template_type)
    entity_name = os.path.basename(entity_path)
    if not os.path.exists(template_path):
        bot.info("entity %s does not have %s." %(entity_name, template_type))
        return None
    
    # Let's keep track of each file
    entity_folders = os.listdir(template_path)

    for entity_folder in entity_folders:
        all_files = os.listdir(template_path)
        valids = []    # valid files, loaded or not

    # Find all valid images
    for folder in entity_folders:
        folder_path = "%s/%s" %(template_path,folder)
        all_files = os.listdir(folder_path)
        for single_file in all_files:
            parts = single_file.split('.')
            full_path = "%s/%s" %(folder_path,single_file)
            ext = '.'.join(parts[1:])
            if ext in acceptable_types:
                valid = {'original': full_path}
                metadata_file = "%s/%s.json" %(folder_path,parts[0])
                if os.path.exists(metadata_file):
                    valid['metadata'] = metadata_file
                valids.append(valid)

    # Warn the user about missing valid files, not logical given folder
    if len(valids) == 0:
        bot.warning("entity %s does not have %s." %(entity_name, template_type))
        return None
    else:
        bot.info("entity %s has %s %s" %(entity_name, len(valids), template_type))

    return valids
