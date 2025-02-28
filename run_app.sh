#! /bin/bash

#docker run -d --rm \
docker run -i -t --rm \
    -v "$(pwd)":/app \
    --user $(id -u):$(id -g) \
    --name geofinder \
    -p 9005:8080 \
    srp33/geofinder \
        python web_app.py
