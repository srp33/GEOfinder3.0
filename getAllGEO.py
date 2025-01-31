from geofetch import Finder
import glob
import gzip
import joblib
import os
import re
import requests
import sys
import time

tmp_dir_path = sys.argv[1]
out_tsv_file_path = sys.argv[2]

gse_obj = Finder()
gse_list = sorted(gse_obj.get_gse_all())

def save_gse(gse):
    try:
        tmp_file_path = f"{tmp_dir_path}/{gse}"

        if os.path.exists(tmp_file_path):
#            print(f"{gse} has already been saved.", flush=True)
            return False
        else:
            print(f"Retrieving metadata for {gse}.", flush=True)

        url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse}&targ=gse&view=quick&form=text"
        gse_text = requests.get(url).text

        gse_lines = [line.rstrip("\n") for line in gse_text.strip().split("\n")]
        #gse_lines = [line for line in gse_lines if line.startswith("!Series") and not (line.startswith("!Series_sample") or line.startswith("!Series_contact"))]
        gse_lines = [line for line in gse_lines if line.startswith("!Series") and not line.startswith("!Series_contact")]
        gse_text = "\n".join(gse_lines)

        with open(tmp_file_path, "w") as tmp_file:
            tmp_file.write(gse_text)

        print(f"Saved metadata for {gse} to {tmp_file_path}.", flush=True)

        time.sleep(1)
        return True
    except:
        print(f"Error occurred for {gse}.", flush=True)
        time.sleep(3)
        return False

def get_gpl_info(gpl):
    url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gpl}&targ=gpl&view=quick&form=text"

    gpl_text = requests.get(url).text

    gpl_dict = {}

    for line in gpl_text.strip().split("\n"):
        if line.startswith("!Platform_title = "):
            gpl_dict["title"] = line.replace("!Platform_title = ", "").strip()
        if line.startswith("!Platform_technology = "):
            gpl_dict["technology"] = line.replace("!Platform_technology = ", "").strip()

    return gpl_dict

def remove_non_ascii(text):
    """Remove non-ASCII characters from the text."""
    return ''.join(char for char in text if ord(char) < 128)

joblib.Parallel(n_jobs=8)(joblib.delayed(save_gse)(gse) for gse in gse_list)

# Sometimes the files are empty. This removes them.
for file_path in glob.glob("Data/tmp/*"):
    if os.path.getsize(file_path) == 0:
        print(f"Removing {file_path} because it is empty.", flush=True)
        os.remove(file_path)

gpl_dict = {}

with gzip.open(out_tsv_file_path, "w") as out_tsv_file:
    header = f"GSE\tTitle\tSummary\tOverall_Design\tExperiment_Type\tYear_Released\tNum_Samples\tGPL\tGPL_Title\tGPL_Technology\tSpecies\tTaxon_ID\tSuperSeries_GSE\tSubSeries_GSEs\tPubMed_IDs\n"
    out_tsv_file.write(header.encode())

#    dataset_save_count = 0

    for in_file_path in sorted(glob.glob(f"{tmp_dir_path}/GSE*")):
        with open(in_file_path) as in_file:
            print(f"Parsing text from {in_file_path}", flush=True)

            gse = os.path.basename(in_file_path)

            gse_text = in_file.read()
            gse_dict = {}
            sample_count = 0

            for line in gse_text.split("\n"):
                line = line.strip()
                if len(line) == 0:
                    continue

                line = line.replace("\t", " ")
                line_items = re.split(" += +", line)

                if len(line_items) < 2:
                    continue

                key = line_items[0]
                key = key.replace("!Series_", "")

                if key == "sample_id":
                    sample_count += 1
                else:
                    value = line_items[1]

                    gse_dict.setdefault(key, []).append(value)

                    subseries_gse = []
                    for x in gse_dict.get("relation", []):
                        if x.startswith("SubSeries of: "):
                            subseries_gse.append(x.replace("SubSeries of: ", ""))
                    gse_dict["subseries_gse"] = subseries_gse

                    superseries_gse = []
                    for x in gse_dict.get("relation", []):
                        if x.startswith("SuperSeries of: "):
                            superseries_gse.append(x.replace("SuperSeries of: ", ""))
                    gse_dict["superseries_gse"] = superseries_gse

            for key, value_list in gse_dict.items():
                if len(value_list) == 1:
                    gse_dict[key] = value_list[0]
                else:
                    gse_dict[key] = "|".join(value_list)

            title = remove_non_ascii(gse_dict["title"])

            if title == "RETIRED": # This happened at least for GSE1829.
                continue

            summary = remove_non_ascii(gse_dict.get("summary", ""))
            overall_design = remove_non_ascii(gse_dict.get("overall_design", ""))
            experiment_type = gse_dict.get("type", "")
            gpl = gse_dict.get("platform_id", "")
            species = gse_dict.get("platform_organism", "")
            taxon_id = gse_dict.get("platform_taxid", "")
            subseries_gse = gse_dict.get("subseries_gse", "")
            superseries_gse = gse_dict.get("superseries_gse", "")
            pubmed_ids = gse_dict.get("pubmed_id", "")
            submission_year = gse_dict.get("submission_date", "").split(" ")[-1]

            # Deal with the fact that some series have multiple platforms.
            for x in gpl.split("|"):
                if x not in gpl_dict:
                    print(f"Getting info for {x}", flush=True)
                    gpl_dict[x] = get_gpl_info(x)

            gpl_title = "|".join(sorted(set([gpl_dict[x]["title"] for x in gpl.split("|") if "title" in gpl_dict[x]])))
            gpl_technology = "|".join(sorted(set([gpl_dict[x]["technology"] for x in gpl.split("|") if "technology" in gpl_dict[x]])))

            out_line = "\t".join([gse, title, summary, overall_design, experiment_type, submission_year, str(sample_count), gpl, gpl_title, gpl_technology, species, taxon_id, subseries_gse, superseries_gse, pubmed_ids]) + "\n"
            out_tsv_file.write(out_line.encode())

#            dataset_save_count += 1

print(f"Saved to {out_tsv_file_path}.")
