#! /bin/bash

DOCKER_BUILDKIT=1 DEVELOPMENT_MODE=False docker build --no-cache -t nexus.gwdc.org.au/meertime/$1:$2 -f docker/meertime_$1.Dockerfile .
docker push nexus.gwdc.org.au/meertime/$1:$2
