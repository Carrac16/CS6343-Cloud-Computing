#!/bin/bash

docker build -t emailserver .
docker tag emailserver:latest matthewp76/emailserver:latest
docker push matthewp76/emailserver
docker image rm emailserver
clear
docker image ls
