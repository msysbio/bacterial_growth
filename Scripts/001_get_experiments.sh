# 1. Obtain the number of unique experiments to then make subdirectories with these names; 
# ------------------------------------------------------------------------------------------
# each directory then contains one subdirecotry per replicate of the experiment
# each experiment directory contains files for growth, metabolites over time, medium...

cd /Users/julia/bacterialGrowth_thesis/IntermediateFiles
awk '{print substr($1,1,length($1)-6)}' lab_files_names_modified.txt | sort | uniq > lab_experiment_names.txt