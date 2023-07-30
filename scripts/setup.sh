#!/bin/bash

VERSION="113.0.5672.24"
RELEASE="https://chromedriver.storage.googleapis.com/${VERSION}/chromedriver_linux64.zip"

sudo apt install -y \
    unzip

# make a tmp directory
mkdir -p tmp;

# download the driver from mozilla
wget ${RELEASE} -O tmp/driver.zip

cd tmp

# unzip the driver in the tmp directory
unzip driver.zip

# install it in the local bin directory
mv chromedriver ~/.local/bin

cd .. && rm -rf tmp;
