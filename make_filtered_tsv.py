import gzip 
import pandas as pd

#filters the AllGEO.tsv.gz file to remove irrelevant species and experiment types. Creates new file filtered_AllGEO.tsv
with gzip.open("AllGEO.tsv.gz", "rt") as read_file: 
    with open("filtered_AllGEO.tsv", "w") as filtered_file:

        line1 = read_file.readline()
        items = line1.rstrip("\n").split("\t")

        #writes column headers to new file
        filtered_file.write("GSE\tSpecies\tExperiment_Type\tNum_Samples\tSamples_Range\tSummary\tYear_Released\tSuperSeries_GSE\tSubSeries_GSE\n")

        # GSE = items[0], experiment = items[4], num_samples = items[6] species = items[10] 
        # Year_Released = items[5], SuperSeries_GSE = [12], SubSeries_GSEs = [13]
        for line in read_file:
            items = line.rstrip("\n").split("\t")
            species = ""
            experiment_type = ""
            super_series = ""
            sub_series = ""
            num_samples = int(items[6])
            samples_range = ""

            #checks the species names
            if("|" in items[10]):
                multiple_species = items[10].split("|")
                if "Homo sapiens" in multiple_species:
                    species = " | ".join(multiple_species)
            elif items[10] == "Homo sapiens":
                    species = items[10]

            #checks the experiment types
            if("|" in items[4]):
                multiple_types = items[4].split("|")
                valid_types = []
                for types in multiple_types:
                    if types == "Expression profiling by high throughput sequencing" or types == "Expression profiling by array":
                        valid_types.append(types)
                valid_types.sort()
                experiment_type = " | ".join(valid_types)    
            else:
                types = items[4]
                if types == "Expression profiling by high throughput sequencing" or types == "Expression profiling by array":
                    experiment_type = types

            #checks if it is a SuperSeries
            if (items[12] == ""):
                super_series = "No"
            else: 
                super_series = "Yes"   

            #checks if it is a SubSeries
            if (items[13] == ""):
                sub_series = "No"
            else:
                sub_series = "Yes"

            #assigns range for num_samples
            if(num_samples <= 10):
                samples_range = "1-10"
            elif(10 < num_samples <= 50):
                samples_range = "11-50"
            elif(50 < num_samples <= 100):
                samples_range = "51-100"
            elif(100 < num_samples <= 500):
                samples_range = "101-500"
            elif(500 < num_samples <= 1000):
                samples_range = "501-1000"
            elif(1000 < num_samples):
                samples_range = "51-100"

            #write the relevant data to filtered_file
            if (species and experiment_type):
                filtered_file.write(f"{items[0]}\t{species}\t{experiment_type}\t{items[6]}\t{samples_range}\t{items[2]}\t{items[5]}\t{super_series}\t{sub_series}\n")

    #list of all unique years in the data:
    #['2001' '2002' '2003' '2004' '2005' '2006' '2007' '2008' '2009' '2010' '2011' '2012' '2013' '2014' '2015' '2016' '2017' '2018' '2019' '2020' '2021' '2022' '2023' '2024']
