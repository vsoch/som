#!/bin/sh

# We need to have curl and fq installed
command_exists () {
    if ! type "$1" > /dev/null; then
        echo "Please install $1 before running this script. Exiting."  
        exit 1
    fi
}

command_exists curl
command_exists jq
command_exists unzip
command_exists zipinfo
command_exists grep
command_exists uniq

# This script will download the updated swagger python client for the SOM API 
download=$(curl -k -X POST -H "content-type:application/json" -d '{"swaggerUrl":"https://app.swaggerhub.com/apiproxy/schema/file/susanweber/UID/1.0.0/swagger.json"}' https://generator.swagger.io/api/gen/clients/python)
code=$(echo $download | jq -r '.code')
download_link=$(echo $download | jq -r '.link')
wget $download_link --no-check-certificate -O $code.zip
folder=$(zipinfo -1 $code.zip | grep -oE '^[^/]+' | uniq)
echo "Extracting $folder..."
unzip -q $code.zip

# Move files to be included in package
mv $folder/swagger_client som/api/client
mv $folder/docs som/api/client/docs
mv $folder/README.md som/api/client
mv $folder/test som/api/client/test
rm -rf $folder
rm $code.zip
