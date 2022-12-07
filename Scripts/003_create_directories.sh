cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles/

echo "" > line.txt


# eliminate header of the file
tail -n +2 ../experiments_info.txt > ../experiments_info_mod.txt

while read -r line; do
    # echo "=========================================="

    echo $line > line.txt

    bacteria=$(awk '{print $5}' line.txt)
    experiment=$(awk '{print $3}' line.txt)
    
    cd ../Data/
    mkdir -p $bacteria
    cd ../Data/$bacteria
    mkdir -p $experiment
    cd ../../IntermediateFiles/
    
done < ../experiments_info_mod.txt

cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles
rm line.txt
# cd ../
# rm experiments_info_mod.txt


cd /Users/julia/bacterialGrowth_thesis/Data

echo "BT:"
ls -lt BT/ | tail -n +2 | wc -l

echo "RI:"
ls -lt RI/ | tail -n +2 | wc -l
