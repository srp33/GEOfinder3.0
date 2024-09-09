import chromadb
import csv
import gzip

chroma_client = chromadb.PersistentClient(path="./collectionFiles")
geo_collection = chroma_client.create_collection(name="geo_collection")

# geo_collection = chroma_client.get_collection(name="geo_collection")
# print(chroma_client.get_ids("geo_collection"))

data_dict = {}

'''
with gzip.open("../AllGEO.tsv.gz") as meta_file:
    line = meta_file.readline()
#     line_items = line.decode().rstrip("\n").split("\t")
#     print(line_items)
    
    for line in meta_file:
        line_items = line.decode().rstrip("\n").split("\t")

        gse = line_items[0]
        summary = line_items[2]
        experiment_type = line_items[4]
        species = line_items[8]

        data_dict[gse] = {"summary": summary, "experiment_type": experiment_type, "species": species}
'''

with gzip.open("../gte-large.tsv.gz") as gse_emb_file:
    for line in gse_emb_file:
        
        line_items = line.decode().rstrip("\n").split("\t")
        gse = line_items[0]
        embedding = line_items[1:]

        # Convert to numbers using a list comprehension.
        embedding = [float(x) for x in embedding]

        geo_collection.add(
            embeddings = embedding,
            ids = gse,
            # documents = data_dict[gse]["summary"],
            # metadatas = {"experiment_type": data_dict[gse]["experiment_type"], "species": data_dict[gse]["species"]}
        )
        
        '''
        embeddings = embedding
        ids = gse
        documents = data_dict[gse]["summary"]
        metadatas = {"experiment_type": data_dict[gse]["experiment_type"], "species": data_dict[gse]["species"]}
        print(f"{embeddings}\n{ids}\n{documents}\n{metadatas}")
        break
        '''




