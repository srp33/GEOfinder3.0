import os
os.environ['HF_HOME'] = "/Models/huggingface"

from bs4 import BeautifulSoup
import chromadb
from chromadb.utils import embedding_functions
import gzip
import re
from sentence_transformers import SentenceTransformer
import shutil
import sys

def clean_text(text):
    text = text.lower()
    text = text.replace("\n", " ") # Remove newline characters
    text = re.sub(r'https?://\S+|www\.\S+', '', text) # Remove URLs
    text = re.sub(r'\W', ' ', str(text)) # Remove non-alphanumeric characters
    text = remove_html_tags(text)
    text = re.sub(r' +', r' ', text) # Remove consecutive spaces
    text = text.strip()

    return text

def remove_html_tags(text):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(text, "html.parser")

    # Extract text without HTML tags
    clean_text = soup.get_text(separator=" ")

    return clean_text

in_tsv_file_path = sys.argv[1]
experiment_types_file_path = sys.argv[2]
species_file_path = sys.argv[3]
checkpoint = sys.argv[4]
embeddings_dir_path = sys.argv[5]

with gzip.open(experiment_types_file_path) as the_file:
    experiment_types = the_file.read().decode().rstrip("\n").split("\n")

with gzip.open(species_file_path) as the_file:
    species = the_file.read().decode().rstrip("\n").split("\n")

model = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=checkpoint)

# Create embedding database.
#shutil.rmtree(embeddings_dir_path)
chroma_client = chromadb.PersistentClient(path = embeddings_dir_path)

embedding_collection = chroma_client.get_or_create_collection(name = "geo_collection")

line_count = 0

with gzip.open(in_tsv_file_path) as in_tsv_file:
    in_tsv_file.readline()

    for line in in_tsv_file:
        line_count += 1
        if line_count % 100 == 0:
            print(f"Obtaining embeddings for line {line_count}.", flush=True)

        line_items = line.decode().rstrip("\n").split("\t")
        gse = line_items[0]

        has_embedding = len(embedding_collection.get(ids=gse)["ids"]) == 1

        if not has_embedding:
            print(f"Saving embedding for {gse}")

            title = line_items[1]
            summary = line_items[2]
            overall_design = line_items[3]
            series_experiment_types = line_items[4].split(" | ")
            year = int(line_items[5])
            samples_range = line_items[7]
            series_species = line_items[8].split(" | ")

            text = clean_text(f"{title} {summary} {overall_design}")
            embedding = model([text])[0].tolist()

            metadatas = {"number_samples_range": samples_range, "year": year}
            for x in experiment_types:
                metadatas[x] = x in series_experiment_types
            for s in species:
                metadatas[s] = s in series_species

            embedding_collection.add(ids = gse, embeddings = embedding, metadatas = metadatas)
