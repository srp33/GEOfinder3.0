#! /bin/bash

set -o errexit

all_geo_tsv_file_path="tsvFiles/AllGEO.tsv.gz"
#all_geo_json_file_path="/Data/AllGEO_Website.json.gz"

mkdir -p tmp/Embeddings

#docker run -i -t --rm \
docker run --rm \
    -v "$(pwd)":/app \
    --user $(id -u):$(id -g) \
    srp33/geofinder \
        python getAllGEO.py /app/tmp "$all_geo_tsv_file_path"
#python prepareAllGEO_Website.py "$all_geo_tsv_file_path" "$all_geo_json_file_path"
#python saveEmbeddings.py "$all_geo_json_file_path" checkpoints2.txt 100000000 "${tmp_dir_path}/Embeddings_Website"

# This puts the embedding in a TSV file rather than JSON so it can be read line by line.
#python reformatEmbeddings.py "${tmp_dir_path}/Embeddings_Website/thenlper/gte-large.gz" "${tmp_dir_path}/Embeddings_Website/thenlper/gte-large.tsv.gz"
exit

docker run -i -t --rm \
    -v "$(pwd)":/app \
    --user $(id -u):$(id -g) \
    srp33/geofinder \
        python make_filtered_tsv.py

rm -rf collectionFiles

docker run -i -t --rm \
    -v "$(pwd)":/app \
    --user $(id -u):$(id -g) \
    srp33/geofinder \
        python make_collection.py
