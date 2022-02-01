#! /bin/bash

sudo DOCKER_BUILDKIT=1 DEVELOPEMENT_MODE=False docker build --no-cache -t nexus.gwdc.org.au/meertime/$1:$2 -f docker/meertime_$1.Dockerfile . 
sudo docker push nexus.gwdc.org.au/meertime/$1:$2
