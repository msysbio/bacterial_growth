# Main directory of the project
cd /Users/julia/bacterialGrowth_thesis/

# Create the directory in which all the intermediate files will be placed
mkdir -p IntermediateFiles/

# Unzip the given data
unzip -oq DataParsed.zip
rm -r __MACOSX

ls -lt

ls -lt  DataParsed/ | grep -i .txt | awk '{print $9}' > IntermediateFiles/lab_files_names.txt
more IntermediateFiles/lab_files_names.txt | wc -l
ls -lt DataParsed/ | grep .txt | wc -lcd /Users/julia/bacterialGrowth_thesis/IntermediateFiles
cp lab_files_names.txt lab_files_names_modified.txtwc -l lab_files_names.txt
wc -l lab_files_names_modified.txt
cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles
awk '{print substr($1,1,length($1)-6)}' lab_files_names.txt | sort | uniq | head
awk '{print substr($1,1,length($1)-6)}' lab_files_names_modified.txt | sort | uniq > lab_experiment_names.txt

wc -l lab_experiment_names.txt

cd /Users/julia/bacterialGrowth_thesis/
rm IntermediateFiles/lab_files_headers.txt

while read -r file;
    do
        head -n 1 DataParsed/$file >> IntermediateFiles/lab_files_headers.txt
done < IntermediateFiles/lab_files_names.txt
cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles/

head lab_files_headers.txt

more lab_files_headers.txt | wc -l
cat lab_files_headers.txt | tr " " "\n" | sort | uniq > lab_headers.txt
head lab_headers.txt
rm experiments_info.txt

echo 'file_name,experiment_name,replicate_number' | column -t -s "," > experiments_info.txt

while read -r file; do

    file_name=$file
    experiment_name=${file_name:0:${#file_name}-6}
    replicate_number=${file_name:${#file_name}-5:1}
    echo $file_name $experiment_name $replicate_number >> experiments_info.txt
    
done < lab_files_names.txt

more experiments_info.txt | wc -l
head experiments_info.txt
tail -n +2 experiments_info.txt > experiments_info_mod.txt
head experiments_info_mod.txt
cd /Users/julia/bacterialGrowth_thesis/
mkdir -p Data/
while read -r line; do

    experiment=$(echo $line | awk '{print $2}')
    replicate=$(echo $line | awk '{print $3}')
    
    file=$(echo $line | awk '{print $1}')
    
    cd /Users/julia/bacterialGrowth_thesis/Data
    mkdir -p $experiment
    mkdir -p $experiment/$replicate

    path_origin=/Users/julia/bacterialGrowth_thesis/DataParsed/"$file"
    path_destination=/Users/julia/bacterialGrowth_thesis/Data/$experiment/$replicate/
    
    cp $path_origin $path_destination

done < IntermediateFiles/experiments_info_mod.txt
