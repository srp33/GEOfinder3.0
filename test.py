import gzip 

with gzip.open("../AllGEO.tsv.gz", "rt") as meta_file:
    i = 0
    for line in meta_file:
        if i != 58:
            line_elements = meta_file.readline().split("\t")
            # print(line_elements[0])
            print(line_elements[5])

            # line 58 of the file has an unreadable charcter (counting the header as a line)
            # line 57, if disclude header


        i += 1