echo "---- Starting to analyse the given data"

# Main directory of the project
cd /Users/julia/bacterialGrowth_thesis/

# Create the directory in which all the intermediate files will be placed
mkdir -p IntermediateFiles/

# Unzip the given data
unzip -oq DataParsed.zip
rm -r __MACOSX

## 1) GET THE LABORATORY FILES' NAMES
ls -lt  DataParsed/ | grep -i .txt | awk '{print $9}' > IntermediateFiles/lab_files_names.txt

cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles
cp lab_files_names.txt lab_files_names_modified.txt

echo "\n---- Obtaining the experiments names..."
awk '{print substr($1,1,length($1)-6)}' lab_files_names_modified.txt | sort | uniq > lab_experiment_names.txt
head lab_experiment_names.txt
echo '...'


cd /Users/julia/bacterialGrowth_thesis/
rm IntermediateFiles/lab_files_headers.txt

echo "\n---- Obtaining the files headers..."
while read -r file;
    do
        head -n 1 DataParsed/$file >> IntermediateFiles/lab_files_headers.txt
done < IntermediateFiles/lab_files_names.txt


cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles/
cat lab_files_headers.txt | tr " " "\n" | sort | uniq > lab_headers.txt

head lab_headers.txt
echo '...'


rm experiments_info.txt
echo "\n---- Obtaining the experiments information..."
echo 'file_name,experiment_name,replicate_number' | column -t -s "," > experiments_info.txt

while read -r file; do

    file_name=$file
    experiment_name=${file_name:0:${#file_name}-6}
    replicate_number=${file_name:${#file_name}-5:1}
    echo $file_name $experiment_name $replicate_number >> experiments_info.txt
    
done < lab_files_names.txt

head experiments_info.txt
echo '...'

tail -n +2 experiments_info.txt > experiments_info_mod.txt

cd /Users/julia/bacterialGrowth_thesis/

echo "\n---- Creating the experiments directories..."
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

echo "\nDONE!\n"
