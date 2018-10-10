#!/usr/bin/python2
# compress bibtex entries from Bibliography.bib to one-lined table form and output to stdout.
# Run from raw directory: `python scripts/bib2tsv.py`

f = open("Citations.bib","r")
bibtex = f.readlines()
f.close()
out = []
counter = 0
current_line = ""
for line in bibtex:
    if line[0] == "@":
        if counter > 0:
            out.append(current_line)
            
        current_line = line.replace("\r","").replace("\n","")
    else:
        current_line += line.replace("\r","").replace("\n","")
    counter += 1
    
out.append(current_line)
for o in out:
    print(o)
        
    
        
    

