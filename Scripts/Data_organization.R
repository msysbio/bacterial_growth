getwd()

experiment_name = "BT_batch_mucin1_1"
df <- read.table("DataParsed/BT/BT_batch_mucin1_1.txt", header=TRUE, sep='', dec = ".")
df

growth_data <- df[,c("time", "OD")]

# Try to automatize this part!
metabolites <- colnames(df)[colnames(df)!=c("time","OD","pH","liquidtotalcount","liquidactivecount","attachedtotalcount")]

metabolites_massSpec <- c("Galactose", "Manose", "Fucose")
metabolites_hplc <-  metabolites[!metabolites_massSpec%in%metabolites]
metabolites_units <- metabolites

for (i in 1:length(metabolites)) {
  if (metabolites[i]%in%metabolites_massSpec) {
    metabolites_units[i] <- paste(metabolites[i], "(mM)")
  } else {
    metabolites_units[i] <- paste(metabolites[i], "(AUC)")
  }
}

metabolites_data <- df[, c("time",metabolites)]
colnames(metabolites_data) <- c("time",metabolites_units)
metabolites_data

system("mkdir -p MT_data/experiments/BT_batch_mucin1_1") # PASS IT AS A PARAMETER


# I put the paste command to then substitute only the file name by a parameter
write.table(growth_data, paste("MT_data/experiments/BT_batch_mucin1_1/", "growth_data", ".txt", sep=""),
            sep = " ", dec = ".",
            row.names = FALSE, col.names = TRUE, quote = FALSE)
write.table(metabolites_data, paste("MT_data/experiments/BT_batch_mucin1_1/", "metabolites_data", ".txt", sep=""),
            sep = " ", dec = ".",
            row.names = FALSE, col.names = TRUE, quote = FALSE)
