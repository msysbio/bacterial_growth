getwd()

FILE = "BT_batch_mucin1_1.txt"

headers <- c("id", "replicate", "bacteria", "biculture", "medium", "mucin", "harvest_time", "pH_initial",
       "carbon_source", "RNA_seq")

df <- data.frame(matrix(vector(), 0, length(headers),
                        dimnames=list(c(), headers)),
                 stringsAsFactors=F)


file_name <- substring(toString(FILE), 1, nchar(toString(FILE))-4)

df[1,"id"] <- substring(toString(FILE), 1, nchar(toString(FILE))-6)   #eliminate extension and rep no.
df[1,"bacteria"] <- substring(toString(file_name), 1, 2)  #gets bacteria from two first characters
df[1,"replicate"] <- substring(toString(file_name), nchar(toString(file_name))-2+2, nchar(toString(file_name)))

# Check if biculture
if (substring(toString(FILE), 4, 5) == "BT") {
  df[1,"biculture"] <- "BT"
} else if (substring(toString(FILE), 4, 5) == "RI"){
  df[1,"biculture"] <- "RI"
} else {
  df[1,"biculture"] <- "no"
}

# Check if MUCIN
if (grepl("mucin", file_name, fixed = TRUE)){
  df[1,"mucin"] <- "yes"
} else {
  df[1,"mucin"] <- "no"
}

# Check if MEDIUM WC
if (grepl("WC", file_name, fixed = TRUE)){
  df[1,"medium"] <- "WC"
}

# Check if CARBON SOURCE
if (grepl("[1-9]C", file_name, fixed = TRUE)){
  df[1,"carbon_source"] <- "yes"
} else {
  df[1,"carbon_source"] <- "no"
}

# Check if RNASeq
if (grepl("RNAseq", file_name, fixed = TRUE)){
  df[1,"RNA_seq"] <- "yes"
} else {
  df[1,"RNA_seq"] <- "no"
}
