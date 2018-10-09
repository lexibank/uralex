#!/usr/bin/python2
# print bibtex entries from tsv Citation_codes.tsv to stdout. Run from raw folder.
# To create bibliography, run `python scripts/tsv2bib.py > Citations.bib`

import csv

out = ""
with open("Citation_codes.tsv","r") as f:
    tsv = csv.reader(f, delimiter="\t",quotechar='"')

    for row in tsv:
        if row[2] == "type": # header
            continue
        if row[2] == "E":    # expert (not citable)
            continue
        
        bibtex_entry = row[1].replace(", ",",\n ") + "\n\n"
        out += bibtex_entry

print(out)

