PROJECT_PATH=$1
FILES_PATH=$2
BIOLOGICAL_REPLICATE_NAME=$3
PERTURBATION_NAME=$4

# Main directory of the project
cd $PROJECT_PATH

# Create the directory in which all the intermediate files will be placed
mkdir -p IntermediateFiles/

## 1) GET THE LABORATORY FILES' NAMES CONTAINED IN THE GIVEN DIRECTORY $FILES_PATH
## ==========================================================================================================================================================================
ls -lt  $FILES_PATH | grep -i .txt | awk '{print $9}' > IntermediateFiles/lab_files_names.txt

cd $PROJECT_PATH'IntermediateFiles'

awk '{print substr($1,1,length($1)-6)}' lab_files_names.txt | sort | uniq > lab_experiment_names.txt

## 2) GET THE HEADERS THAT ARE ON ALL THE GIVEN FILES
## ==========================================================================================================================================================================
rm -f lab_files_headers.txt

while read -r file;
    do
        head -n 1 $FILES_PATH$file >> lab_files_headers.txt
done < lab_files_names.txt

cat lab_files_headers.txt | tr " " "\n" | sort | uniq > lab_headers.txt

## 3) GET BIOLOGICAL_REPLICATE INFORMATION TO CREATE THE DIRECTORIES
## ==========================================================================================================================================================================
rm -f experiments_info.txt
echo 'file_name,experiment_name,replicate_number' | column -t -s "," > experiments_info.txt

while read -r file; do

    file_name=$file
    experiment_name=${file_name:0:${#file_name}-6}
    replicate_number=${file_name:${#file_name}-5:1}
    echo $file_name $experiment_name $replicate_number >> experiments_info.txt
    
done < lab_files_names.txt


tail -n +2 experiments_info.txt > experiments_info_mod.txt

cd $PROJECT_PATH

## 4) CREATE THE DIRECTORIES
## ==========================================================================================================================================================================
mkdir -p Data/
mkdir -p Data/experiments/
rm -f $PROJECT_PATH'IntermediateFiles/listOfFiles.list'
while read -r line; do

    cd $PROJECT_PATH

    experiment=$BIOLOGICAL_REPLICATE_NAME
    replicate=$(echo $line | awk '{print $3}')
    
    file=$(echo $line | awk '{print $1}')
    path_origin=$FILES_PATH$file

    cd $PROJECT_PATH'Data/experiments'
    mkdir -p $experiment

    if [ ! -z "$PERTURBATION_NAME" ]
    then
        perturbation=$PERTURBATION_NAME
        mkdir -p $experiment/$perturbation
        mkdir -p $experiment/$perturbation/$replicate
        path_destination=$PROJECT_PATH'Data/experiments/'$experiment/$perturbation/$replicate/
    else
        mkdir -p $experiment/$replicate
        path_destination=$PROJECT_PATH'Data/experiments/'$experiment/$replicate/
    fi
    
    final_file=$path_destination$file
    echo $final_file >> $PROJECT_PATH'IntermediateFiles/listOfFiles.list'

    cp $path_origin $path_destination

done < IntermediateFiles/experiments_info_mod.txt

cd $PROJECT_PATH'IntermediateFiles'
rm experiments_info.txt
rm experiments_info_mod.txt
rm lab_experiment_names.txt
rm lab_files_headers.txt
rm lab_files_names.txt
