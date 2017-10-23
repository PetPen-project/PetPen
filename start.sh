#!/bin/bash

docker run -d -it --restart=always -p 1880:1880 --name sinica-nodered project:sinica-nodered
nvidia-docker run -d -it --restart=always --name sinica-django --net host project:sinica-django
