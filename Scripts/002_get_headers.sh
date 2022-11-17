# To check the number of files (= number of headers)
a=$(more IntermediateFiles/lab_files_names.txt | wc -l)

# To count the number of headers
b=$(ls -lt DataParsed/ | grep .txt | wc -l)

if [[ (! -f IntermediateFiles/lab_files_headers.txt) || $a -ne $b ]]; 
then
    echo "Writing the lab_files_headers.txt file..."
    
    while read -r file;
    do
        head -n 1 DataParsed/$file >> IntermediateFiles/lab_headers.txt
    done < IntermediateFiles/lab_files_names.txt
fi
echo "lab_files_headers.txt file prepared:"
wc -l IntermediateFiles/lab_files_headers.txt

cat IntermediateFiles/lab_files_headers.txt | tr " " "\n" | sort | uniq > IntermediateFiles/lab_headers.txt

### 
# TO DO: SEPARATE FILES SOMEHOW DEPENDING ON THE FIELDS THEY HAVE -> Or not?
# DO THIS AFTER GETTING THE DICTIONARY WITH THE EXPERIMENTS INFO TO MKDIR DEPENDING ON THE COLUMNS
###
