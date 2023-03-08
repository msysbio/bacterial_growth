# 1. Get files names
# ------------------------------------------------------------------------------------------
cd /Users/julia/bacterialGrowth_thesis/

ls -lt  DataParsed/ | grep -i .txt | awk '{print $9}' > IntermediateFiles/lab_files_names.txt

more IntermediateFiles/lab_files_names.txt | wc -l
ls -lt DataParsed/ | grep .txt | wc -l

# 2. Modifcations in files names
# ------------------------------------------------------------------------------------------

cd IntermediateFiles/
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