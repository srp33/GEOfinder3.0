import mkDataFrames
import chromadb
import numpy as np
   

def filter_by_metas(metadata_dct):
        
        print("in filter_by_metas, metadata= \n", metadata_dct)

        # Get metadata dataframes: species, num samples, platform
        #print("about to make species_frame")
        species_frame = mkDataFrames.make_dataframe("Species")
        #print("og species_frame: \n", species_frame)
        num_samples_frame = mkDataFrames.make_numsamples_dataframe()
        experiment_frame = mkDataFrames.make_dataframe("Experiment_Type")
        #print("og experiment_frame: \n", experiment_frame)

        summary_frame = mkDataFrames.make_summary_dataframe()

        #print("in filter_by_metas, species frame:", species_frame)

        # print("testing for IDS: ", species_frame["GSE"].to_list())

        match_ids = []

        #filters each individual dataFrame based on the user's selections
        if metadata_dct["Species"]:
            #print("in if-statement, initial species frame=\n", species_frame)
            #for species in metadata_dct["Species"]
            species_frame = species_frame[species_frame["Species"].isin(metadata_dct["Species"])]
            #print("in if-statement, post species frame=\n", species_frame)
        species_frame = species_frame.groupby("GSE")["Species"].agg(lambda lst: ", ".join(lst)).reset_index()
        #print("species_frame, post-filtering: \n", species_frame)
        #this is a problem - *** empty dataframe 

        if metadata_dct["Num_Samples"]:
            #print(type(metadata_dct["Num_Samples"]))
            num_samples_frame = num_samples_frame[num_samples_frame["Num_Samples"].isin(metadata_dct["Num_Samples"])]
        num_samples_frame = num_samples_frame.groupby("GSE")["Num_Samples"].agg(lambda lst: ", ".join(lst)).reset_index()
        #print("samples_frame, post-filtering: \n", num_samples_frame)
        
        if metadata_dct["Experiment_Type"]:
            experiment_frame = experiment_frame[experiment_frame["Experiment_Type"].isin(metadata_dct["Experiment_Type"])]
        experiment_frame = experiment_frame.groupby("GSE")["Experiment_Type"].agg(lambda lst: ", ".join(lst)).reset_index()
        #print("experiment_frame: \n", experiment_frame)

        
        join_frame = species_frame.merge(summary_frame, how="inner") # add summaries to filtered frame
        join_frame = join_frame.merge(num_samples_frame, how="inner") # only save ids present in all filtered frames
        join_frame = join_frame.merge(experiment_frame, how="inner")


        #print("\n\n join frame: \n: ", join_frame["Experiment_Type"].tail(30))
        #return list(set(join_frame["GSE"].to_list()))

        #print("in filter_by_metas, frame= \n", join_frame)
        return join_frame
           
# metadata = {"Species": ["Homo sapiens", "Mus musculus"], "Num_Samples": ["1-10"]}
# filter_by_metas(metadata)

# print(filter_by_metas(metadata))

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