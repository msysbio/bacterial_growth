
# Get organisms dictionary from JensenLab FTP server
curl -O https://download.jensenlab.org/organisms_dictionary.tar.gz
tar -zxvf organisms_dictionary.tar.gz
mv organisms_dictionary/* .
rmdir organisms_dictionary organisms_dictionary.tar.gz

# Create groups from the organisms files (returns growthDB_groups.tsv)
./create_groups.pl

# Filter unicellular taxa, keeping their NCBI Taxonomy Ids (returns growthDB_unicellular_ncbi.tsv)
./filter_unicellular_ncbi.awk  METdb_GENOMIC_REFERENCE_DATABASE_FOR_MARINE_SPECIES.csv  growthDB_groups.tsv  >  growthDB_unicellular_ncbi.tsv

# Make an overall file with NCBI Taxonomy Ids and their corresponding preferred names:
file1="organisms_entities.tsv"
file2="organisms_preferred.tsv"
awk -F "\t" 'BEGIN { OFS="\t" } NR == FNR { file1_org_ids[$1] = 1; file1_ncbi_ids[$1] = $3; next } $1 in file1_org_ids { print file1_ncbi_ids[$1], $2 }' "$file1" "$file2" > ncbi_ids_preferred_names.tsv
# sed -i 's/ /\t/' ncbi_ids_preferred_names.tsv

# Keep the NCBI Taxonomy Ids returned from the `filter_unicellular_ncbi.awk` script which are present in the `organisms_entities.tsv`:
file1="growthDB_unicellular_ncbi.tsv"
file2="organisms_entities.tsv"
awk -F "\t"  'NR == FNR { file1_entries[$1] = 1; next } $3 in file1_entries { print $3 }' "$file1" "$file2" > unicellular_ncbi_ids.tsv

# Get only NCBI Taxonomy Ids along with their corresponding preferred names of the unicellular taxa:
file1="unicellular_ncbi_ids.tsv"
file2="ncbi_ids_preferred_names.tsv"
awk 'BEGIN { OFS = "\t" } NR == FNR { file1_ncbi_ids[$1] = 1 ; next } $1 in file1_ncbi_ids { print $0 }' "$file1" "$file2" > unicellular_ncbi_ids_preferred_names.tsv

