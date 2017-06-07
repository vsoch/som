#!/usr/bin/env python

'''

validators.py: validation of folders and compressed objects for wordfish standard

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

def validate_dataset(dataset,testing_base=None,clean_up=True):
    '''validate_dataset is a general function to take a compressed object 
    (zip or .targz) or folder and run the correct validation functions depending
    on the input type.
    :param dataset: the full path to the dataset
    :param testing_base: the testing_base directory
    :param clean_up: whether to clean up the directory upon finish
    '''
    if os.path.isdir(dataset):
        valid = validate_folder(folder=dataset)
    elif re.search("[.]zip$|[.]tar[.]gz$",dataset):
        valid = validate_compressed(compressed_file=dataset,
                                    testing_base=testing_base,
                                    clean_up=clean_up)
    return valid


def validate_folder(folder):
    '''validate_folder will ensure the folder provided is reflective of WordFish standard
    :param folder: the folder to validate, corresponding to a collection base
    :returns valid: True/False
    '''    

    # The first level should have folders with collections
    valid = True
    full_path = os.path.abspath(folder)

    if validate_metadata(full_path) == False:        
        valid = False

    # validate images, text, and metadata of the entities
    valid_entities = validate_entities(full_path)
    if valid_entities == None:
        bot.error("found invalid collection: does not have entities.")
        valid = False        
    elif valid_entities == False:
        bot.error("found invalid collection: invalid entities.")
        valid = False        
    else:
        print("collection %s is valid." %folder)        

    return valid


def validate_metadata(full_path,metadata_type=None):
    '''validate_metadata checks to see if a name (either a collection
    name, folder for an image or text) has associated metadata, indicated by
    a file of the same name (ending with json) in the parent directory of the
    named file. If no matching files are found, None is returned, and the user
    is alerted. If a matching file is found, it is checked to be valid json.
    :param full_path: full path to a file or folder
    :param metadata_type: either one of collection, image, or text. Default collection
    '''
    if metadata_type == None:
        metadata_type = "collection"

    parent_dir = os.path.dirname(full_path)
    base_name = os.path.basename(full_path).split('.')[0]
    metadata = "%s/%s.json" %(parent_dir,base_name)

    if os.path.exists(metadata):
        bot.debug('found %s metadata: %s' %(metadata_type, base_name))
        try:
            md = read_json(metadata)
            bot.info('%s %s metadata is valid' %(metadata_type, base_name))
        except:
            bot.error('%s %s has invalid json metadata %s' %(metadata_type, base_name, metadata))
            return False
 
    else:
        bot.info('%s %s does not have metadata file %s.json' %(metadata_type, base_name, base_name))
        return None

    return True


def validate_entities(full_path):
    '''validate_entities will check to see if each subdirectory (an entity
    in a collection) has a set of valid images and text objects. The user
    is alerted about extraneous files.
    :param full_path: the full path to the collection folder with entities
    '''
    valid = True
    entities = os.listdir(full_path)
    bot.info("Found %s entities in collection." %len(entities))
    if len(entities) == 0:
        return None
     
    for entity in entities:
        entity_path = "%s/%s" %(full_path,entity)

        # Does the entity have metadata?
        if validate_metadata(entity_path,"entity") == False:      
            valid = False

        entity_texts = validate_texts(entity_path)
        entity_images = validate_images(entity_path)

        # If images and text are empty for a collection, invalid
        if entity_texts == None and entity_images == None:
            bot.error("found invalid entity: does not have images or text.")
            valid = False

        # if either text or images are not valid, entities considered invalid
        if entity_texts == False or entity_images == False:
            bot.error("entity %s does not have valid images or text." %(entity))
            valid = False

    return valid


def validate_texts(entity_path,acceptable_types=None):
    '''validate_texts will check an entity directory
    for a text folder. If it exists, each subfolder will be assessed for
    correct wordfish structure and metadata
    :param entity_path the path to the top level (entity) folder
    :param acceptable_types: the valid extensions to allow
    '''    
    if acceptable_types == None:
        acceptable_types = ['txt']

    valid = validate_template(entity_path=entity_path, 
                              template_type="text",
                              acceptable_types=acceptable_types)
    return valid



def validate_images(entity_path, acceptable_types=None):
    '''validate_images will check an entity directory
    for an images folder. If it exists, each subfolder will be assessed for
    correct wordfish structure and metadata
    :param entity_path the path to the top level (entity) folder
    :param acceptable_types: the valid extensions to allow
    '''
    
    if acceptable_types == None:
        acceptable_types = ['dcm','png','jpg','jpeg','nii','nii.gz']

    valid = validate_template(entity_path=entity_path, 
                              template_type="images",
                              acceptable_types=acceptable_types)
    return valid


def validate_template(entity_path, template_type, acceptable_types):
    '''validate_template will check an entity directory
    for an folder of a particular type, for files and metadata that
    meet a particular criteria. If needed, additional parsing
    functions can be passed to this function. 
    :param entity_path the path to the top level (entity) folder
    :param template_type: should be one of images or text
    :param acceptable_types: the valid extensions to allow
    '''
    valid = True
    template_path = "%s/%s" %(entity_path,template_type)
    entity_name = os.path.basename(entity_path)
    if not os.path.exists(template_path):
        bot.info("entity %s does not have %s." %(entity_name, template_type))
        return None
    
    # Let's keep track of each file
    all_folders = os.listdir(template_path)
    valids = []    # valid files
    others = []    # Not valid as metadata or accepted

    # Find all valid images
    for folder in all_folders:
        folder_path = "%s/%s" %(template_path,folder)
        all_files = os.listdir(folder_path)
        for single_file in all_files:
            file_path = "%s/%s" %(folder_path,single_file)
            parts = single_file.split('.')
            ext = '.'.join(parts[1:])
            if ext in acceptable_types:
                valids.append(file_path)
            else:
                others.append(file_path)

    # Warn the user about missing valid files, not logical given folder
    if len(valids) == 0:
        bot.warning("entity %s does not have %s." %(entity_name, template_type))
        return None
    else:
        bot.info("entity %s has %s %s" %(entity_name, len(valids), template_type))

    # Parse through the "others" and alert user about invalid file
    valid_metadata = 0
    invalid_metadata = 0
    skipped_files = 0    

    # Assess each valid for metadata
    for contender in valids:
        if validate_metadata(contender,template_type) == False:      
            bot.error("metadata %s for entity %s is invalid" %(contender,entity_name))
            invalid_metadata +=1
            valid = False
        else:
            valid_metadata +=1
    else:
        skipped_files +=1      
        bot.warning("%s for %s/%s is not valid for import and is ignored" %(contender, entity_name, template_type))

    bot.info("found %s valid metadata, %s invalid metadata, and %s skipped files for %s" %(valid_metadata,
                                                                                           invalid_metadata,
                                                                                           skipped_files,
                                                                                           entity_name))
    return valid


def validate_compressed(compressed_file,testing_base=None,clean_up=True):
    '''validate_compressed will first decompress a file to a temporary location,
    and then test if the folder is valid given the WordFish standard.
    :param compressed_file: the file to first extract.
    :param testing_base: If not given, a temporary location will be created. Otherwise,
    a folder will be made in testing_base.
    :param clean_up: clean up (remove) extracted files/folders after test. Default True
    '''
    if testing_base == None:
        testing_base = tempfile.mkdtemp()
 
    valid = True
    dest_dir = tempfile.mkdtemp(prefix="%s/" %testing_base)
    if compressed_file.endswith('.tar.gz'):
        test_folder = untar_dir(compressed_file,dest_dir)
 
    elif compressed_file.endswith('.zip'):
        test_folder = unzip_dir(compressed_file,dest_dir)

    else:
        bot.error("Invalid compressed file type: %s, exiting." %compressed_file)
        sys.exit(1)

    # Each object in the folder (a collection)
    collections = os.listdir(test_folder)
    bot.info("collections found: %s" %len(collections))
    for collection in collections:
        collection_path = "%s/%s" %(test_folder,collection)
        if validate_folder(collection_path) == False:
            bot.error("collection %s is invalid." %collection)

    if clean_up == True:
        shutil.rmtree(dest_dir)
    return valid
