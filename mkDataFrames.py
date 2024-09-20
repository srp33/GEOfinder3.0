import pandas as pd 
import gzip 
from io import StringIO

'''
def make_numsamples_dataframe():
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
'''