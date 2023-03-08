library(dplyr)

getwd()
setwd('/Users/julia/bacterialGrowth_thesis/')

experiments_info <- read.table("experiments_info.txt", header=TRUE, sep='', dec = ".")
files_names <- read.table('IntermediateFiles/lab_files_names.txt', header = FALSE, sep = "", dec = ".")[,1]

for (i in 1:length(files_names)) {
# for (i in c(2)) {
  
  # 1. Create the two df with growth and metabolite data, respectively
  FILE = files_names[i]
  df <- read.table(paste("DataParsed/", FILE, sep=""), header=TRUE, sep='', dec = ".")
  df
  
  growth_data <- df[,c("time", "OD")]
  
  # Try to automatize this part!
  metabolites <- colnames(df)[!colnames(df) %in% c("time","OD","pH","liquidtotalcount","liquidactivecount","attachedtotalcount")]
  
  if(length(metabolites) > 0){
    metabolites_massSpec <- c("Galactose", "Manose", "Fucose")
    metabolites_hplc <-  metabolites[!metabolites_massSpec%in%metabolites]
    metabolites_units <- metabolites
    
    for (j in 1:length(metabolites)) {
      if (metabolites[j]%in%metabolites_massSpec) {
        metabolites_units[j] <- paste(metabolites[j], "(mM)")
      } else {
        metabolites_units[j] <- paste(metabolites[j], "(AUC)")
      }
    }
    
    metabolites_data <- df[, c("time",metabolites)]
    colnames(metabolites_data) <- c("time",metabolites_units)
    metabolites_data
  }
  
  # 2. Construct the directory
  bacteria_dir <- paste(experiments_info[i,5], "/", sep="")
  experiment_dir <- paste(experiments_info[i,3], "/", sep="")
  replicate_dir <- paste(experiments_info[i,2], "/", sep="")
  
  data_dir <- paste('Data/experiments/', bacteria_dir, experiment_dir, replicate_dir, sep="")
  
  # 3. Save the new data in the data_dir (specific for each replicate)
  write.table(growth_data, paste(data_dir, "growth_data.txt", sep=""),
              sep = " ", dec = ".",
              row.names = FALSE, col.names = TRUE, quote = FALSE)
  if(length(metabolites) > 0){
    write.table(metabolites_data, paste(data_dir, "metabolites_data.txt", sep=""),
                sep = " ", dec = ".",
                row.names = FALSE, col.names = TRUE, quote = FALSE)
  }
}
