#! /bin/bash

# docker run -i -t --rm \
#     -v "$(pwd)":/app \
#     --user $(id -u):$(id -g) \
#     srp33/geofinder \
#         python make_filtered_tsv.py

docker run -i -t --rm \
    -v "$(pwd)":/app \
    --user $(id -u):$(id -g) \
    srp33/geofinder \
        python make_collection.py