#!/usr/bin/python2
# print bibtex entries from tsv Citation_codes.tsv to stdout. Run from raw folder.
# To create bibliography, run `python scripts/tsv2bib.py > Citations.bib`
import re
import csv
import argparse

from pybtex.database import parse_string

BREAK_PATTERN = re.compile(',\s+(?P<key>[a-z]+)\s*=')
PARSER_DESC = "Convert citation entries tsv files to BibTeX output."
parser = argparse.ArgumentParser(description=PARSER_DESC)

parser.add_argument("-b", "--borr_ref",
                    dest="borr_ref",
                    help="Use borrowing reference file instead of citations file.",
                    default=False,
                    action='store_true')

args = parser.parse_args()
if args.borr_ref == True:
    tsvfile = "Borrowing_references.tsv"

else:
    tsvfile = "Citation_codes.tsv"

out = []
with open(tsvfile,"r") as f:
    for row in csv.reader(f, delimiter="\t",quotechar='"'):
        if row[2] == "type": # header
            continue
        if row[2] == "E":    # expert (not citable)
            continue

        bib = BREAK_PATTERN.sub(lambda m: ',\n {0}='.format(m.group('key')), row[1])
        parse_string(bib, bib_format='bibtex')
        out.append(bib)

print('\n\n'.join(out))
