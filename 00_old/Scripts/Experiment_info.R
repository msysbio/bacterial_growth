getwd()

system("ls -lt IntermediateFiles/")

files_names <- read.table('IntermediateFiles/lab_files_names.txt', header = FALSE, sep = "", dec = ".")[,1]
files_names_mod <- read.table('IntermediateFiles/lab_files_names_modified.txt', header = FALSE, sep = "", dec = ".")[,1]
files_df <- data_frame(files=files_names, files_modified=files_names_mod)

# In the modified files I added a low bar to separate the two names of the bacteria

info_headers <- c("file_name", "id", "experiment", "replicate", "bacteria", "biculture", "medium", "mucin", "harvest_time", "pH_initial",
             "carbon_source", "RNA_seq")

experiments_df <- data.frame(matrix(vector(), dim(files_df)[1], length(info_headers),
                           dimnames=list(c(), info_headers)),
                    stringsAsFactors=F)


for (i in 1:length(files_names)) {
  FILE = files_names_mod[i]
  
  experiments_df[i,"file_name"] <- FILE
  experiments_df[i,"id"] <- substring(FILE, 1, nchar(FILE)-4)
  experiments_df[i,"experiment"] <- substring(FILE, 1, nchar(FILE)-6)   #eliminate extension and rep no.
  experiments_df[i,"bacteria"] <- substring(FILE, 1, 2)  #gets bacteria from two first characters
  experiments_df[i,"replicate"] <- substring(FILE, nchar(FILE)-4, nchar(FILE)-4)
  
  # Check if biculture
  if (substring(FILE, 4, 5) == "BT") experiments_df[i,"biculture"] <- "BT"
  else if (substring(FILE, 4, 5) == "RI") experiments_df[i,"biculture"] <- "RI"
  else experiments_df[i,"biculture"] <- "no"
  
  # Check if MUCIN
  if (grepl("mucin", FILE)) experiments_df[i,"mucin"] <- "yes"
  else experiments_df[i,"mucin"] <- "no"
  
  # Check if MEDIUM WC
  if (grepl("WC", FILE))experiments_df[i,"medium"] <- "WC"
  
  # Check if CARBON SOURCE
  if (grepl("[1-9]C", FILE)) experiments_df[i,"carbon_source"] <- "yes"
  else experiments_df[i,"carbon_source"] <- "no"
  
  # Check if RNASeq
  if (grepl("RNAseq", FILE)) experiments_df[i,"RNA_seq"] <- "yes"
  else experiments_df[i,"RNA_seq"] <- "no"
}

save(experiments_df,file="experiments_info.Rda")
write.table(experiments_df, paste("experiments_info", ".txt", sep=""),
            sep = " ", dec = ".",
            row.names = FALSE, col.names = TRUE, quote = FALSE)









