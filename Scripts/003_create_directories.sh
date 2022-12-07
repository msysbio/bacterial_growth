cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles/

echo "" > created_bacteria_directories.txt
echo "" > created_experiment_directories.txt
echo "" > line.txt

# eliminate header of the file
tail -n +2 ../experiments_info.txt > ../experiments_info_mod.txt
echo $(wc -l experiments_info_mod.txt)

while read -r line; do
    echo "=========================================="
    echo "Nueva vuelta"

    echo $line > line.txt

    # cd ../IntermediateFiles/
    bacteria=$(awk '{print $5}' line.txt)
    count=$(more created_bacteria_directories.txt | grep $bacteria | wc -l)

    echo $bacteria
    echo $count
    
    if [ $count == 0 ];
    then
        cd ../Data/
        mkdir -p $bacteria
        echo "created $bacteria"
        cd ../IntermediateFiles/
        echo $bacteria >> created_bacteria_directories.txt
    fi

    # cd ../IntermediateFiles/
    experiment=$(awk '{print $3}' line.txt)
    count2=$(more created_experiment_directories.txt | grep $experiment | wc -l)

    echo $experiment
    echo $count2
    
    if [ $count2 == 0 ];
    then
        cd ../Data/$bacteria
        mkdir -p $experiment
        echo "created $experiment"
        cd ../../IntermediateFiles/
        echo $experiment >> created_experiment_directories.txt
    fi
    
done < ../experiments_info_mod.txt

cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles
rm line.txt
# cd ../
# rm experiments_info_mod.txt