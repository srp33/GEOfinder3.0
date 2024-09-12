import gzip 
import pandas as pd

with gzip.open("../AllGEO.tsv.gz", "rt") as read_file:
    
    with open("species.tsv", "w") as species_file, \
        open("experiment_types.tsv", "w") as experiment_file, \
        open("num_samples.tsv", "w") as num_samples_file:

        line1 = read_file.readline()
        items = line1.rstrip("\n").split("\t")
        # print(items)

        species_file.write("GSE\tSpecies\n")
        experiment_file.write("GSE\tExperiment_Type\n")

        # GSE = items[0], experiment = items[4], num_samples = items[6], species = items[10]
        for line in read_file:
            items = line.rstrip("\n").split("\t")

            #Note to Abby: If you want, you can make this one function for both species and experiment filtering :)
            #make species tsv file:
            if("|" in items[10]):
                multiple_species = items[10].split("|")
                for species in multiple_species:
                    if species == "Homo sapiens":
                        species_file.write(f"{items[0]}\t{species}\n")
            else:
                species = items[10]
                if species == "Homo sapiens":
                    species_file.write(f"{items[0]}\t{items[10]}\n")
            
            ''' should we do this? (it would be outside of the for loop and we would need to create another)
            #merge homo sapien filtered data with allGEO file by GEO ID before filtering out experiment types
            species_df = pd.read_csv('species.tsv', sep='\t')
            allGEO_df = pd.read_csv('../AllGEO.tsv.gz', compression='gzip', sep='\t', on_bad_lines='warn')
            '''

            #make experiment type tsv file:
            if("|" in items[4]):
                multiple_types = items[4].split("|")
                for types in multiple_types:
                    if types == "Expression profiling by high throughput sequencing" or types == "Expression profiling by array":
                        experiment_file.write(f"{items[0]}\t{types}\n")
            else:
                types = items[4]
                if types == "Expression profiling by high throughput sequencing" or types == "Expression profiling by array":
                    experiment_file.write(f"{items[0]}\t{types}\n")



        species_df = pd.read_csv('species.tsv', sep='\t')
        experiment_df = pd.read_csv('experiment_types.tsv', sep='\t')
        # Merge the dataframes based on a common column
        filtered_df = pd.merge(species_df, experiment_df, on='GSE')
        # Write the merged dataframe to a new TSV file
        filtered_df.to_csv('filtered_file.tsv', sep='\t', index=False)

        allGEO_df = pd.read_csv('../AllGEO.tsv.gz', compression='gzip', sep='\t', on_bad_lines='warn')
        filtered_allGEO = pd.merge(filtered_df, allGEO_df, on=['GSE', 'Species', 'Experiment_Type'])
        filtered_allGEO.to_csv('filtered_allGEO.tsv', sep='\t', index=False)

        ''' chatgpt solution that doesnt exactly work either
        merged_df = pd.merge(filtered_df, allGEO_df, on='GSE', how='left', suffixes=('', '_allGEO'))
        # Overwrite specific columns with data from filtered_df
        # Assuming you want to overwrite columns that may have '_allGEO' suffix
        for col in ['Species', 'Experiment_Type']:
            if col + '_allGEO' in merged_df.columns:
                merged_df[col] = merged_df[col + '_allGEO']
                merged_df.drop(columns=[col + '_allGEO'], inplace=True)

        # Write the final result to a new TSV file
        merged_df.to_csv('filtered_allGEO.tsv', sep='\t', index=False)
        '''


#make num samples tsv file
with open("filtered_allGEO.tsv", "r") as read_file:

    with open("num_samples.tsv", "w") as num_samples_file:

        line1 = read_file.readline()
        items = line1.rstrip("\n").split("\t")

        # GSE = items[0], experiment = items[4], num_samples = items[6], species = items[10]
        for line in read_file:
            try:
                items = line.rstrip("\n").split("\t")
                num_samples = int(items[7])
                if num_samples > 0 and num_samples < 11:
                    num_samples_file.write(f"{items[0]}\t1-10\n")
                elif num_samples < 51:
                    num_samples_file.write(f"{items[0]}\t11-50\n")
                elif num_samples < 101:
                    num_samples_file.write(f"{items[0]}\t51-100\n")
                elif num_samples < 501:
                    num_samples_file.write(f"{items[0]}\t101-500\n")
                elif num_samples < 1001:
                    num_samples_file.write(f"{items[0]}\t501-1000\n")
                else:
                    num_samples_file.write(f"{items[0]}\t1000+\n")
            except:
                num_samples_file.write(f"{items[0]}\terror\n")










            



        
       


        

    

