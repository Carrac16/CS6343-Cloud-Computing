#!/bin/bash

docker build -t emailclient .
docker tag emailclient:latest matthewp76/emailclient:latest
docker push matthewp76/emailclient
docker image rm emailclient
clear
docker image ls
