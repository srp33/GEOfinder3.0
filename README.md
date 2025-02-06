# GEOfinder

This repository contains the source code and build scripts for the GEOfinder web application. This application enables researchers to search for data series in [Gene Expression Omnibus](https://www.ncbi.nlm.nih.gov/geo/) (GEO). For now, it only supports searching for transcriptomic data series.

You can find a working instance of the app [here](https://bioapps.byu.edu/geofinder).

Please submit an issue if you have a question or suggestion.

### Running the app locally

Although Docker containers can be run on many operating systems, these instructions are specific to Linux-based operating systems.

1. Execute the build script: `bash build.sh`. This creates the Docker image for the app.
2. Execute the data-preparation script: `bash prepare_data.sh`. This script retrieves data from GEO and builds an embedding database. It takes many hours to complete.
3. Start the app: `bash run_app.sh`. Follow the instructions at the terminal to access the app through your browser.
