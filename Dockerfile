# I had an issue with the sqlite3 version for the latest version of chromadb, but I am using an older verson of Python for now.
FROM python:3.9.21

RUN pip install cherrypy==18.10.0 chromadb geofetch==0.12.5 transformers==4.37.2 sentence-transformers==2.4.0 tensorflow==2.18

RUN mkdir -p /huggingface \
 && chmod 777 /huggingface -R

WORKDIR /app
