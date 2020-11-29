#!/bin/bash

docker build -t spamdetection .
docker tag spamdetection:latest matthewp76/spamdetection:latest
docker push matthewp76/spamdetection
docker image rm spamdetection
clear
docker image ls
