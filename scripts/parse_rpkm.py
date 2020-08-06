import re
import sys

#usage 'python calculate_rpkm.py mapped.counted.result total_reads_file srrID'
'''
# exampe of mapped.count.result:
NODE_8_length_295416_cov_86.298909  read_length_150    1805
NODE_9_length_294755_cov_77.048012  read_length_150     267
NODE_10_length_287310_cov_147.7697  read_length_150     2469

# total_reads_file; total reads number in each sample
10004483	SRR7768473
10005994	SRR7768567
10007320	SRR7768664

# srrID is just the srrID sample ID number (such as SRR7768473)
'''

count_result = sys.argv[1]
total_reads_file = sys.argv[2]
srr = sys.argv[3]
outfile = srr + "rpkm.txt"

def total(srr):
    with open(total_reads_file) as f:
        lines = f.readlines()

    for line in lines:
        if line.find(srr) != -1:
            reads = line.strip().split("\t")
            return reads[0]
    f.close()

with open(count_result) as file_object:
    rows = file_object.readlines()

with open(outfile,'w') as out_object:
    for row in rows:
        groups = row.strip().split()
        node = groups[0].split('_')
        counts = int(groups[2])
        length = int(node[3])
        totals = int(total(srr))
        rpkm = counts/(length/1000*totals/1e6)
        
        out_object.write(groups[0] + "\t" + str(totals) + "\t" + str(counts) + "\t" + str(length) + "\t"+ str(rpkm) + "\n")
        

