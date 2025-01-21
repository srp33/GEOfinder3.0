# GEOfinder

This repository contains the source code and build scripts for the GEOfinder web application. This application enables researchers to search for data series in [Gene Expression Omnibus](https://www.ncbi.nlm.nih.gov/geo/) (GEO). For now, it only supports searching for transcriptomic data series.

You can find a working instance of the app [here](https://bioapps.byu.edu/geofinder).

Please submit an issue if you have a question or suggestion.

### Running the app locally

Although Docker containers can be run on many operating systems, these instructions are specific to Linux-based operating systems.

1. Execute the build script: `bash build.sh`.
2. Create a subdirectory called `tsvFiles`.
3. Copy `AllGEO.tsv.gz` into the `tsvFiles` directory. If you do not have this file, contact us.
4. Copy `gte-large.tsv.gz` into the `tsvFiles` directory. If you do not have this file, contact us.
5. Prepare the TSV data: `bash prepare_data.sh`.
6. Start the app: `bash run_app.sh`.
7. Follow the instructions at the terminal.