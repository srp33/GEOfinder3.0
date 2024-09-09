import pandas as pd 
import gzip 
from io import StringIO

#makes dataframes for the columns that have string values 
def make_dataframe(meta):

    print("in make_dataframe with ", meta)

### This code is for a functional file, without unreadable characters (most recent AllGEO throws an error)
#    with gzip.open("../AllGEO1.tsv.gz", "rt") as meta_file:

#         data_frame = pd.read_csv(meta_file, sep="\t", nrows=300) 
    

### This code is to work with the broken file :)
    with gzip.open("../AllGEO.tsv.gz", "rt") as meta_file:
        lines = [next(meta_file) for n in range(50)]
        lines_str = "".join(lines)
        lines_as_file = StringIO(lines_str)
        data_frame = pd.read_csv(lines_as_file, sep="\t")
        
### workaround code ends here

        meta_frame = data_frame[["GSE", meta]] 
        print(meta_frame)

        '''
        for i in range(meta_frame.shape[0]):
            row = meta_frame.iloc[i]
            if "|" in row[meta]:
                duplicate_list = row[meta].split("|")
                separate_data = []
                for duplicate in duplicate_list:
                    separate_data.append((row["GSE"], duplicate))
                separated_meta_frame = pd.DataFrame(data=separate_data, columns=("GSE",meta))
                meta_frame.drop(i, inplace=True)
                i -= 1
                meta_frame = pd.concat(objs=[meta_frame,separated_meta_frame], ignore_index=True)
        meta_frame.sort_values(by=["GSE"], inplace=True, ignore_index=True)
        '''
        return meta_frame

#print(make_dataframe("Species").value_counts())

def make_numsamples_dataframe():
### This code is for a functional file, without unreadable characters (most recent AllGEO throws an error)
#     with gzip.open("../AllGEO.tsv.gz", "rt") as meta_file:
        # data_frame = pd.read_csv(meta_file, sep="\t") # uncomment this with working file:  , nrows=300) 
    

### This code is to work with the broken file :)
    with gzip.open("../AllGEO.tsv.gz", "rt") as meta_file:
        lines = [next(meta_file) for n in range(50)]
        lines_str = "".join(lines)
        lines_as_file = StringIO(lines_str)
        data_frame = pd.read_csv(lines_as_file, sep="\t")
### workaround code ends here

        samples_frame = data_frame[["GSE", "Num_Samples"]] 
        
        samples_frame["Num_Samples"] = samples_frame["Num_Samples"].astype(str) 

    for index, row in samples_frame.iterrows():
        num_samples = int(row["Num_Samples"])

        if num_samples > 0 and num_samples < 11:
            samples_frame.iloc[index,1] = "1-10"
        elif num_samples < 51:
            samples_frame.iloc[index,1] = "11-50"
        elif num_samples < 101:
            samples_frame.iloc[index,1] = "51-100"
        elif num_samples < 501:
            samples_frame.iloc[index,1] = "101-500"
        elif num_samples < 1001:
            samples_frame.iloc[index,1] = "501-1000"
        else:
            samples_frame.iloc[index,1] = "1000+"
   
    return samples_frame

# print(make_numsamples_dataframe())

def make_summary_dataframe():
### This code is for a functional file, without unreadable characters (most recent AllGEO throws an error)
#     with gzip.open("../AllGEO.tsv.gz", "rt") as meta_file:
        # data_frame = pd.read_csv(meta_file, sep="\t") # uncomment this with working file:  , nrows=300) 
    

### This code is to work with the broken file :)
    with gzip.open("../AllGEO.tsv.gz", "rt") as meta_file:
        lines = [next(meta_file) for n in range(50)]
        lines_str = "".join(lines)
        lines_as_file = StringIO(lines_str)
        data_frame = pd.read_csv(lines_as_file, sep="\t")
### workaround code ends here

        return data_frame[["GSE", "Summary"]]
    
# print(make_summary_dataframe())