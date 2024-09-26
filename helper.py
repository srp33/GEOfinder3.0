import chromadb
import numpy as np
import pandas as pd
   
#returns a dataframe, filtered based on the user's selections
def filter_by_metas(metadata_dct):
        
    with open("filtered_AllGEO.tsv", "r") as meta_file:
        data_frame = pd.read_csv(meta_file, sep="\t") 

    df_copy = data_frame.copy(deep=True)

    #filtering the dataframe copy based on experiment type
    if(metadata_dct["Experiment_Type"]):
        if(len(metadata_dct["Experiment_Type"])==1):
            if(metadata_dct["Experiment_Type"][0]=="Microarray"):
                df_copy = df_copy[df_copy["Experiment_Type"].str.startswith("Expression profiling by array")]
            elif(metadata_dct["Experiment_Type"][0]=="RNA sequencing"):
                df_copy = df_copy[df_copy["Experiment_Type"].str.endswith("Expression profiling by high throughput sequencing")]
        
    #filtering the dataframe copy based on number of samples
    if(metadata_dct["Num_Samples"]):
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
        df_copy = pd.merge(df_copy, num_samples_df, on = 'GSE')   
        df_copy["Species"] =  df_copy["Species_x"].combine_first(df_copy["Species_y"])
        df_copy["Num_Samples"] =  df_copy["Num_Samples_x"].combine_first(df_copy["Num_Samples_y"])
        df_copy["Summary"] =  df_copy["Summary_x"].combine_first(df_copy["Summary_y"])
        df_copy["Experiment_Type"] =  df_copy["Experiment_Type_x"].combine_first(df_copy["Experiment_Type_y"])
        df_copy.drop(columns=["Species_x", "Species_y", "Summary_x", "Summary_y", "Num_Samples_x", "Num_Samples_y", "Experiment_Type_x", "Experiment_Type_y"], inplace=True)
    
    return df_copy

#returns a dictionary of the closest results to the user IDs input
def generate_id_query_results(input_ids):

    print("in generate_id_query_results, ids:", input_ids)

    chroma_client = chromadb.PersistentClient(path="./collectionFiles")
    my_collection = chroma_client.get_collection(name="geo_collection")
    
    input_embeddings = []

    for id in input_ids:
        data_dict = my_collection.get(ids=id, include=["embeddings"])
        input_embeddings.append(data_dict["embeddings"][0])

    input_embeddings = np.array(input_embeddings)
    avg_embedding = np.mean(input_embeddings, axis=0).tolist()

    num_results = 50
    # similarityResults = my_collection.query(query_embeddings=avg_embedding, n_results=num_results)
    similarityResults = my_collection.query(query_embeddings=avg_embedding, n_results=num_results)
    #print(f"\n\nSimilarity Results: {similarityResults}\n")
    return similarityResults["ids"][0]

#returns a list of all GSE ID's in the filtered_AllGEO.tsv file 
def generate_database_ids():
    database_ids = []
    with open("filtered_AllGEO.tsv", "r") as filtered_file:
        line1 = filtered_file.readline()
        for line in filtered_file:
            items = line.split("\t")
            database_ids.append(items[0])
    return database_ids
