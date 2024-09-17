import gzip 
import pandas as pd

with gzip.open("../AllGEO.tsv.gz", "rt") as read_file: 
    with open("filtered_AllGEO.tsv", "w") as filtered_file:

        line1 = read_file.readline()
        items = line1.rstrip("\n").split("\t")

        filtered_file.write("GSE\tSpecies\tExperiment_Type\tNum_Samples\tSummary\n")

        # GSE = items[0], experiment = items[4], num_samples = items[6], species = items[10]
        for line in read_file:
            items = line.rstrip("\n").split("\t")
            species = ""
            experiment_type = ""

            #define the species name
            if("|" in items[10]):
                multiple_species = items[10].split("|")
                if "Homo sapiens" in multiple_species:
                    species = " | ".join(multiple_species)
            elif items[10] == "Homo sapiens":
                    species = items[10]

            #define the experiment type
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

            #write the data to filtered_file
            if (species and experiment_type):
                filtered_file.write(f"{items[0]}\t{species}\t{experiment_type}\t{items[6]}\t{items[2]}\n")