import re
import sys

#usage 'python calculate_rpkm.py mapped.counted.result total_reads_file srrID'
'''
# exampe of mapped.count.result:
    
>k141_1136180 flag=1 multi=5.0000 len=1251 read_length_150 read_count_210
>k141_1647461 flag=1 multi=15.0000 len=1424 read_length_150 read_count_248
>k141_1704270 flag=1 multi=12.0000 len=1498 read_length_150 read_count_212
>k141_1249798 flag=1 multi=18.4768 len=1586 read_length_150 read_count_458


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
    out_object.write("scaffold_name\tTotal_reads\tmapped_reads\tscaffold_length\tRPKM\n")
    for row in rows:
        groups = row.strip().split()
        scaffold_name = groups[0].replace(">", "")
        counts = int(groups[5].replace("read_count_", ""))
        length = int(groups[3].replace("len=", ""))
        totals = int(total(srr))
        rpkm = float(counts/(length/1000*totals/1e6))
        
        out_object.write(scaffold_name + "\t" + str(totals) + "\t" + str(counts) + "\t" + str(length) + "\t"+ str(rpkm) + "\n")
        

