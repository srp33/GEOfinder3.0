import chromadb
import numpy as np
import pandas as pd
   
def filter_by_metas(metadata_dct):
        
    with open("filtered_AllGEO.tsv", "r") as meta_file:
        data_frame = pd.read_csv(meta_file, sep="\t") 

    df_copy = data_frame.copy(deep=True)
    print("Df copy:", df_copy)

    if(metadata_dct["Experiment_Type"]):
        print(metadata_dct["Experiment_Type"])
        df_copy = df_copy[df_copy["Experiment_Type"].startswith("Expression profiling by array" | df_copy["Experiment_Type"].endswith("Expression profiling by high throughput sequencing"))]
        print(df_copy.head())
    
    if(metadata_dct["Num_Samples"]):
        print(metadata_dct["Num_Samples"])
        #dataFrame3 = dataFrame[(dataFrame["Height"] < 72) & (dataFrame["Weight"] > 200)]

    match_ids = []

    return df_copy


'''
Want to test if faster to query, then filter by metadatas, or to filter the collection by metadatas, then query.
'''


#returns a dictionary of the closest results to the user IDs input
def generate_id_query_results(input_ids):

    print("in generate_id_query_results")

    # print("\n\ngenerate_id_query_results: input ids\n", input_ids)

    chroma_client = chromadb.PersistentClient(path="./collectionFiles")
    my_collection = chroma_client.get_collection(name="geo_collection")

    print("*******************")
    print("collection length: ", len(my_collection))
    print("*******************")
    
    input_embeddings = []
    # print(f"input embeddings before for loop: {input_embeddings}")
    for id in input_ids:
        # print(f"in for loop, id: {id}")
        data_dict = my_collection.get(ids=id, include=["embeddings"])
        input_embeddings.append(data_dict["embeddings"][0])

    input_embeddings = np.array(input_embeddings)

    avg_embedding = np.mean(input_embeddings, axis=0).tolist()


    num_results = 50
    # similarityResults = my_collection.query(query_embeddings=avg_embedding, n_results=num_results)
    similarityResults = my_collection.query(query_embeddings=avg_embedding, n_results=num_results)

    #print(f"\n\nSimilarity Results: {similarityResults}\n")
    return similarityResults["ids"][0]


fake_dictionary = {"Species":[], "Experiment_Type":[],"Num_Samples":[]}

filter_by_metas(fake_dictionary)

'''
#returns a dictionary of the closest results to the user's keyword input
def generate_keyword_query_results(words):

    for i in range(100-len(words)):
        words += " the"
    
    chroma_client = chromadb.PersistentClient(path="./collectionFiles")
    my_collection = chroma_client.get_collection(name="geo_collection")
    
    num_results = 50
    similarityResults = my_collection.query(query_texts=[words], n_results=num_results)
    # print("\n\nin generate keyword results, similarity results: ", similarityResults)

    formatted_dict = {}
    for i in range(num_results):
        formatted_dict[similarityResults['ids'][0][i]] = {"Description": similarityResults['documents'][0][i]}
                                                        #    "Species": similarityResults['metadatas'][0][i]['Species'], \
                                                        #         "# Samples": similarityResults['metadatas'][0][i]['Num_Samples'], \
                                                        #             "Experiment Type": similarityResults['metadatas'][0][i]['Experiment_Type']}
    return list(formatted_dict.keys())
''' 