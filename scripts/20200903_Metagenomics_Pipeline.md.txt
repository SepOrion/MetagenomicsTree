######################################
###Preprocessing raw sequence reads###
######################################

for n in *.fastq
do
	/home/suginoka/Metagenomics_Programs/bbmap/bbduk.sh in=$n out=$n"_output.fastq" ref=/home/suginoka/Metagenomics_Programs/bbmap/resources/adapters.fa ktrim=r k=23 mink=11 hdist=1 tpe tbo
done

##Remove artifacts
for n in *output.fastq
do
/home/suginoka/Metagenomics_Programs/bbmap/bbduk.sh in=$n out=$n"_u.fastq" outm=$n"_m.fastq" ref=/home/suginoka/Metagenomics_Programs/bbmap/resources/sequencing_artifacts.fa.gz ref=/home/suginoka/Metagenomics_Programs/bbmap/resources/phix174_ill.ref.fa.gz k=31 hdist=1 stats=$n"_stats.txt"
done

######################
###Error correction###
######################

##This is tadpole; use this if the dataset is large
for n in *u.fastq
do
/home/suginoka/Metagenomics_Programs/bbmap/tadpole.sh in=$n out=$n"_ec.fastq" ecc=t passes=1 prefilter int=t
done

##############
###Assembly###
##############

##Megahit
/home/suginoka/Metagenomics_Programs/MEGAHIT-1.2.9-Linux-x86_64-static/bin/megahit --12 merged.fastq_output.fastq_u.fastq_ec.fastq -o merged.fastq_output.fastq_u.fastq_ec.fastq_assembly.fastq


############################
###Calculate Mapping Rate###
############################

#We use pullseq and bowtie2 to scaffold, align and map the number of aligned reads
#Here, we're selecting scaffolds that are >=1000 bp 
#Note: Need to change "$n/final.contigs.fa" if metaspades was used. I think the file you want is called "contigs.fasta". May also be the "scaffold.fasta" file; need to check

for n in *assembly.fastq
do
/home/suginoka/Metagenomics_Programs/pullseq/src/pullseq -i $n/final.contigs.fa -m 1000 > $n"_sequence_min1000.fastq"
done 

##Create bowtie2 index
##NOTE: May need to go into bowtie2-build file and change the first line from calling python3 to calling python
module load python
for n in *min1000.fastq
do
mkdir $n".min"
/home/suginoka/Metagenomics_Programs/bowtie2-2.4.1-linux-x86_64/bowtie2-build $n $n".min"/sequence_min1000
done

##Reformat paired reads
for n in *ec.fastq
do
/home/suginoka/Metagenomics_Programs/bbmap/reformat.sh in=$n out1=$n"_read1.fastq" out2=$n"_read2.fastq"
done

##Paired read alignment
for n in *ec.fastq
do
/home/suginoka/Metagenomics_Programs/bowtie2-2.4.1-linux-x86_64/bowtie2 -x merged.fastq_output.fastq_u.fastq_ec.fastq_assembly.fastq_sequence_min1000.fastq.min/sequence_min1000 -1 $n"_read1.fastq" -2 $n"_read2.fastq" -S $n"_alignment.sam" -p 19
done

#######################
###RPKM Calculations###
#######################

##N50, N90 calculation
##I have no idea what this is for
for n in *assembly.fastq
do
/home/suginoka/Metagenomics_Programs/bbmap/stats.sh in=$n/final.contigs.fa out=$n"_assembly_data_stats"
done

##Count mapped reads
for n in *alignment.sam
do
/home/suginoka/Metagenomics_Programs/shrinksam/shrinksam -i $n > $n"_mapped.sam"
done

module load Ruby
for n in *output.fastq
do
/home/suginoka/Metagenomics_Programs/misc_scripts/add_read_count/add_read_count.rb $n"_u.fastq_ec.fastq_alignment.sam_mapped.sam" $n"_u.fastq_ec.fastq_assembly.fastq_sequence_min1000.fastq" > $n"_mapped.fasta.counted"
grep -e ">" $n"_mapped.fasta.counted" > $n"_mapped.counted.result"
done

##Collect total mapped reads
touch mapped_reads_collected.txt
for n in *mapped.counted.result
do
echo $n | sed 's/.fastq_output.fastq_mapped.counted.result//g' | cat >> mapped_reads_collected.txt
sed 's/.*_count_//g' $n | paste -sd+ - | bc >> mapped_reads_collected.txt
done

##Collect total reads
touch total_reads_collected.txt
for n in *_stats.txt
do
grep -e "File\|Total" $n | cat >> total_reads_collected.txt
done

##Make total read file for RPKM calculations
for n in *output.fastq
do
grep -e "Total" $n"_stats.txt" | cat >> $n"_total_reads"
done
sed -i 's/\#Total	//g' $n"_total_reads"

##Set up files for RPKM calculation
for n in *counted.result
do
sed 's/read_count_\|>\|flag.*read_len//g' $n | cat >> $n"_scaffold.txt"
done


#RPKM Calcs; doesn't work yet
module load python
for n in *output.fastq
do
python /home/suginoka/Metagenomics_Programs/parse_scaffolds_rpkm.py $n"scaffold.txt" total_reads names
done


#####################
###Gene Prediction###
#####################

for n in *min1000.fastq
do
/home/suginoka/Metagenomics_Programs/Prodigal/prodigal -a $n"_trans_protein.fasta" -i $n -p meta -o $n"_predicted.gdk"
done

################
###Annotation###
################

##KEGG Annotation
ln -s /home/suginoka/Metagenomics_Programs/kofam_scan/ruby/bin/ruby

module load Ruby
module load GNU/4.9.3-2.25
export OMP_NUM_THREADS=10
for n in *protein.fasta
do
/home/suginoka/Metagenomics_Programs/kofam_scan/exec_annotation -o $n".Coassembly_KO.txt" $n --tmp-dir=tmp_KO --cpu=10
done