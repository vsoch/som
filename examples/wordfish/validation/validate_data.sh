#!/bin/bash

# This example will show how to validate a particular wordfish folder, targz, etc.
# It assumes that we have installed the som tools, and have the executable som-validator
# on our path
# 
# pip install som

# Print help for the user
som-validator --help

# Let's validate a folder, corresponding to the top of a collection
# (note, the files haven't been put here publicly yet)
git clone http://www.github.com/radinformations/wordfish-standard
cd wordfish-standard

# Here we have a folder with files
tree data

# We can validate it by giving it to the som-validator
som-validator --test data

# We can tell it to be quiet
som-validator --test data --quiet

# We can also validate a compressed object
som-validator --test data.zip

# .. including .tar.gz
som-validator --test data.tar.gz
