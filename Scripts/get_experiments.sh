# 1. Obtain the number of unique experiments to then make subdirectories with these names; 
# each directory then contains one subdirecotry per replicate of the experiment
# each experiment directory contains files for growth, metabolites over time, medium...

# This is for obtaining the name of the experiments !!!

cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles
awk '{print substr($1,1,length($1)-6)}' lab_files_names.txt | sort | uniq > lab_experiment_names.txt

# 2. Modifcations in files names

a=$(more lab_files_names.txt | wc -l)
b=$(more lab_files_names_modified.txt | wc -l)

if [[ (! -f lab_files_names_modified.txt) || $a -ne $b ]]; 
then
    rm lab_files_names_modified.txt
    while read -r file;
    do
    # re = $'^[A-Z]+$'
        if [[ ${file:2:1} =~ ^[A-Z]+$ ]] ; 
        then
            len=$(echo $file | wc -c)
            echo -e ${file:0:2}_${file:2:$len} >> lab_files_names_modified.txt
        else
            # echo "entro en el ELSE"
            echo -e $file >> lab_files_names_modified.txt
        fi

    done < lab_files_names.txt
fi

wc -l lab_files_names.txt
wc -l lab_files_names_modified.txt