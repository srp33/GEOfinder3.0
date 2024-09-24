import chromadb
import numpy as np
import pandas as pd
   
def filter_by_metas(metadata_dct):
        
    with open("filtered_AllGEO.tsv", "r") as meta_file:
        data_frame = pd.read_csv(meta_file, sep="\t") 

    df_copy = data_frame.copy(deep=True)
    

    if(metadata_dct["Experiment_Type"]):
        if(len(metadata_dct["Experiment_Type"])==1):
            if(metadata_dct["Experiment_Type"][0]=="Microarray"):
                df_copy = df_copy[df_copy["Experiment_Type"].str.startswith("Expression profiling by array")]
            elif(metadata_dct["Experiment_Type"][0]=="RNA sequencing"):
                df_copy = df_copy[df_copy["Experiment_Type"].str.endswith("Expression profiling by high throughput sequencing")]
        
    if(metadata_dct["Num_Samples"]):
        print("Print metadata_dct[Num_Samples]: ", metadata_dct["Num_Samples"])
        #make an empty dataframe
        num_samples_df = pd.DataFrame()

        #add selected sample numbers to dataframe
        if("1-10" in metadata_dct["Num_Samples"]):
            num_samples_df = pd.concat([num_samples_df, df_copy[df_copy["Num_Samples"] <= 10]], ignore_index = True)
        if("11-50" in metadata_dct["Num_Samples"]):
            num_samples_df = pd.concat([num_samples_df, df_copy[(df_copy["Num_Samples"] > 10) & (df_copy["Num_Samples"] <= 50)]], ignore_index = True)
        if("51-100" in metadata_dct["Num_Samples"]):
            num_samples_df = pd.concat([num_samples_df, df_copy[(df_copy["Num_Samples"] > 50) & (df_copy["Num_Samples"] <= 100)]], ignore_index = True)
        if("101-500" in metadata_dct["Num_Samples"]):
            num_samples_df = pd.concat([num_samples_df, df_copy[(df_copy["Num_Samples"] > 100) & (df_copy["Num_Samples"] <= 500)]], ignore_index = True)
        if("501-1000" in metadata_dct["Num_Samples"]):
            num_samples_df = pd.concat([num_samples_df, df_copy[(df_copy["Num_Samples"] > 500) & (df_copy["Num_Samples"] <= 1000)]], ignore_index = True)
        if("1000+" in metadata_dct["Num_Samples"]):
            num_samples_df = pd.concat([num_samples_df, df_copy[df_copy["Num_Samples"] > 1000]], ignore_index = True)
            
        #merge num_samples and df_copy - ASK DR. PICCOLO if there's a better way
        print("df_copy before merging: \n", df_copy.head(10))
        df_copy = pd.merge(df_copy, num_samples_df, on = 'GSE')   
        df_copy["Species"] =  df_copy["Species_x"].combine_first(df_copy["Species_y"])
        df_copy["Num_Samples"] =  df_copy["Num_Samples_x"].combine_first(df_copy["Num_Samples_y"])
        df_copy["Summary"] =  df_copy["Summary_x"].combine_first(df_copy["Summary_y"])
        df_copy["Experiment_Type"] =  df_copy["Experiment_Type_x"].combine_first(df_copy["Experiment_Type_y"])
        df_copy.drop(columns=["Species_x", "Species_y", "Summary_x", "Summary_y", "Num_Samples_x", "Num_Samples_y", "Experiment_Type_x", "Experiment_Type_y"], inplace=True)
        
        print("df_copy after merging: \n", df_copy.head(10))
        print(df_copy.columns)

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
    #print("collection length: ", len(my_collection))
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