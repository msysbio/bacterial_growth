install.packages("dplyr")       # Install dplyr package
library("dplyr") 

setwd('/Users/julia/bacterialGrowth_thesis/')

# =============================================================================
# All lab data
# =============================================================================
files <- list.files('DataParsed/', pattern = "(^BT|^RI).*\\.txt$", all.files=T, full.names=F)
files 

headers <- read.table('DataParsed_original/all_uniq_headers.txt', header = FALSE, sep = "", dec = ".")[,1]
headers

for (i in 1:length(files)) {
  
  df <- read.table(paste("DataParsed_original/", files[i],sep=""), header=TRUE, sep='', dec = ".")
  
  empty_df <- data.frame(matrix(vector(), dim(df)[1], length(headers),
                                dimnames=list(c(), headers)),
                         stringsAsFactors=F)
  
  new_df <- cbind(df, empty_df[!colnames(empty_df) %in% colnames(df)])
  new_df <- new_df %>%dplyr::select("time","OD", everything())
  
  file <- substring(toString(files[i]), 1, nchar(toString(files[i]))-4)
  
  system("mkdir -p DataParsed_original_merged")
  write.table(new_df, paste("DataParsed_original_merged/", file, ".txt", sep=""), 
              sep = " ", dec = ".",
              row.names = FALSE, col.names = TRUE, quote = FALSE)
}
