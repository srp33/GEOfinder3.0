# I had an issue with the sqlite3 version for the latest version of chromadb, but I am using an older verson of Python for now.
FROM python:3.9.21

RUN pip install cherrypy==18.10.0 chromadb pandas

WORKDIR /app
