#! /bin/bash

docker run -i -t --rm \
    -v "$(pwd)":/app \
    --user $(id -u):$(id -g) \
    --name geofinder \
    -p 8080:8080 \
    srp33/geofinder \
        python web_app.py
