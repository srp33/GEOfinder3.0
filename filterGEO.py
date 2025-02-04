import gzip
import os
import sys

in_tsv_file_path = sys.argv[1]
out_tsv_file_path = sys.argv[2]

experiment_types_dict = {}
species_dict = {}

with gzip.open(in_tsv_file_path) as in_tsv_file:
    in_tsv_file.readline()

    for line in in_tsv_file:
        line_items = line.decode().rstrip("\n").split("\t")

        experiment_type = line_items[4].lower().split("|")
        species = line_items[8].lower().split("|")

        for x in experiment_type:
            if x not in experiment_types_dict:
                experiment_types_dict[x] = 0
            experiment_types_dict[x] += 1

        for s in species:
            if s not in species_dict:
                species_dict[s] = 0
            species_dict[s] += 1

top_experiment_types = set()
for experiment_type, count in experiment_types_dict.items():
    if count >= 1000:
        top_experiment_types.add(experiment_type)

#top_experiment_types = sorted(experiment_types_dict, key=experiment_types_dict.get, reverse=True)[:20]
#for experiment_type in top_experiment_types:
#    print(experiment_type, experiment_types_dict[experiment_type])

top_species = set()
for species, count in species_dict.items():
    if count >= 1000:
        top_species.add(species)

#top_species = sorted(species_dict, key=species_dict.get, reverse=True)[:50]
#for species in top_species:
#    print(species, species_dict[species])

with gzip.open(in_tsv_file_path) as in_tsv_file:
    with gzip.open(out_tsv_file_path, "w") as out_tsv_file:
        out_tsv_file.write(in_tsv_file.readline())

        lineCount = 0
        for line in in_tsv_file:
            lineCount += 1
            line_items = line.decode().rstrip("\n").split("\t")

            experiment_type = line_items[4].lower().split("|")
            species = line_items[8].lower().split("|")

            keep_experiment_type = False
            for x in experiment_type:
                if x in top_experiment_types:
                    keep_experiment_type = True
                    break

            keep_species = False
            for s in species:
                if s in top_species:
                    keep_species = True
                    break

            if keep_experiment_type and keep_species:
                out_tsv_file.write(line)
