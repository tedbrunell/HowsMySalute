#!/bin/bash

# Grab the base image
CONTAINER=$(buildah from ubi8/python-39)
echo $CONTAINER

# Mount the container
MNT=$(buildah mount $CONTAINER)
echo $MNT

# Install virtual environment
python3 -m venv install $MNT/env
source $MNT/env/bin/activate
echo "installed venv"

# Install dependencies.
pip3 install --upgrade pip
pip3 install --prefix=$MNT/usr mediapipe
pip3 install --prefix=$MNT/usr flask
pip3 install --prefix=$MNT/usr matplotlib

# Install Files
cp app.py $MNT/
cp HowsMySalute.py $MNT/
mkdir $MNT/templates/
cp templates/index.html $MNT/templates/

# Configure the Container
buildah config --entrypoint 'python3 app.py'

buildah commit $CONTAINER tbrunell/salute
