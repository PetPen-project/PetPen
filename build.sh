#!/bin/bash

docker build -t project:sinica-django -f Dockerfile.django .
docker build -t project:sinica-nodered -f Dockerfile.nodered .
