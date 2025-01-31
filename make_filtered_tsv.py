import gzip

print("Preparing TSV files for use in the app...")

#filters the AllGEO.tsv.gz file to remove irrelevant species and experiment types. Creates new file filtered_AllGEO.tsv
with gzip.open("./tsvFiles/AllGEO.tsv.gz", "r") as read_file:
    with gzip.open("./tsvFiles/filtered_AllGEO.tsv.gz", "w") as filtered_file:
        with gzip.open("./tsvFiles/filtered_AllGEO_ids.tsv.gz", "w") as ids_file:
            line1 = read_file.readline().decode()
            items = line1.rstrip("\n").split("\t")

            ids_file.write("GSE\n".encode())

            #writes column headers to new file
            filtered_file.write("GSE\tSpecies\tExperiment_Type\tNum_Samples\tSamples_Range\tSummary\tYear_Released\tSuperSeries_GSE\tSubSeries_GSE\n".encode())

            # GSE = items[0], experiment = items[4], num_samples = items[6] species = items[10]
            # Year_Released = items[5], SuperSeries_GSE = [12], SubSeries_GSEs = [13]
            for line in read_file:
                items = line.decode().rstrip("\n").split("\t")
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

                #checks if the row contains a SuperSeries, which means it is a SubSeries
                if (items[12] == ""):
                    sub_series = "No"
                else:
                    sub_series = "Yes"

                #checks if the row contains a SubSeries, meaning it is a SuperSeries
                if (items[13] == ""):
                    super_series = "No"
                else:
                    super_series = "Yes"

                #assigns range for num_samples
                if num_samples <= 0:
                    samples_range = "N/A"
                elif num_samples <= 10:
                    samples_range = "1-10"
                elif 10 < num_samples <= 50:
                    samples_range = "11-50"
                elif 50 < num_samples <= 100:
                    samples_range = "51-100"
                elif 100 < num_samples <= 500:
                    samples_range = "101-500"
                elif 500 < num_samples <= 1000:
                    samples_range = "501-1000"
                elif num_samples > 1000:
                    samples_range = "1000+"

                #write the relevant data to filtered_file
                if (species and experiment_type):
                    filtered_file.write(f"{items[0]}\t{species}\t{experiment_type}\t{items[6]}\t{samples_range}\t{items[2]}\t{items[5]}\t{super_series}\t{sub_series}\n".encode())
                    ids_file.write(f"{items[0]}\n".encode())

with gzip.open("./tsvFiles/gte-large.tsv.gz", "r") as read_file:
    with gzip.open("./tsvFiles/gte_ids.tsv.gz", "w") as write_file:
        write_file.write("GSE\n".encode())

        for line in read_file:
            items = line.decode().split("\t")
            write_file.write(f"{items[0]}\n".encode())
