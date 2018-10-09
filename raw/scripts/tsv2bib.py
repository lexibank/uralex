#!/usr/bin/python2
# print bibtex entries from tsv Citation_codes.tsv to stdout. Run from raw folder.
# To create bibliography, run `python scripts/tsv2bib.py > Citations.bib`
import re
import csv

from pybtex.database import parse_string

BREAK_PATTERN = re.compile(',\s+(?P<key>[a-z]+)\s*=')


out = []
with open("Citation_codes.tsv","r") as f:
    for row in csv.reader(f, delimiter="\t",quotechar='"'):
        if row[2] == "type": # header
            continue
        if row[2] == "E":    # expert (not citable)
            continue

        bib = BREAK_PATTERN.sub(lambda m: ',\n {0}='.format(m.group('key')), row[1])
        parse_string(bib, bib_format='bibtex')
        out.append(bib)

print('\n\n'.join(out))
