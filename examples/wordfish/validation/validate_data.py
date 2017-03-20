#!/use/bin/env python

# This example will show how to use the som validator from within python

import os 

# If you want to control the debug level, change MESSAGELEVEL in your 
# environment

# Eg, only print critical information.
os.environ['MESSAGELEVEL'] = "CRITICAL"

from som.wordfish.validators import validate_dataset

# File
compressed_file = "data.zip"
valid = validate_dataset(compressed_file)

# Folder
folder_path = os.path.abspath("data")
valid = validate_dataset(folder_path)
