import re
import sys

#usage 'python select_best_KO.py kofamscan_result.txt ko_dictionary.txt'

kofam = sys.argv[1]
outfile = sys.argv[2]


ko_list = {}

with open(kofam) as ko_object:
    for line in ko_object.readlines():
        if (line[0] == "*"):
            groups = line.strip().split()
            protein = groups[1]
            #print protein
            ko = groups[2]
            if ko_list.get(protein) == None:
                ko_list[protein] = [ko]
ko_object.close()

f = open(outfile, 'w')

for k, v in ko_list.items():
	f.write(str(k)+"\t"+ ",".join([str(x) for x in v]) + "\n")	
	
