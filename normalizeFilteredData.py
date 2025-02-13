import gzip
import sys

tsv_file_path = sys.argv[1]
out_dir_path = sys.argv[2]

# Get the unique values
all_exp_types = set()
all_species = set()

with gzip.open(tsv_file_path) as tsv_file:
    tsv_file.readline().decode()

    for line in tsv_file:
        line_items = line.decode().rstrip("\n").split("\t")

        for exp_type in line_items[4].split(" | "):
            all_exp_types.add(exp_type)

        for species in line_items[8].split(" | "):
            all_species.add(species)

print(all_exp_types)
print(all_species)

#    with open(f"{out_dir_path}/Experiment_Types.tsv", "w") as exp_types_file:
#        with open(f"{out_dir_path}/Species.tsv", "w") as species_file:
