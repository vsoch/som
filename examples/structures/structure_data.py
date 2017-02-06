#!/use/bin/env python

# This example will show how to generate wordfish standard datastructures from
# within python. The basic data structures return paths to objects (images and text)
# and it's up to the application to decide how to read/move etc.

import os 

# If you want to control the debug level, change MESSAGELEVEL in your 
# environment

# Eg, only print critical information.
os.environ['MESSAGELEVEL'] = "CRITICAL"

u

# File
compressed_file = "data.zip"
valid = validate_compressed(compressed_file)

# Folder
folder_path = os.path.abspath("data")
valid = validate_folder(folder_path)
