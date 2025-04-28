library("growthrates")
library("jsonlite")

args <- commandArgs(TRUE)

input_csv   = args[1]
output_json = args[2]

data <- read.table(input_csv, header=T, sep=',')

model_fit <- fit_easylinear(data$time, data$value)
coefficients = coef(model_fit)

f <- file(output_json)
writeLines(c(
           '{',
           paste('"y0":',    coefficients['y0'], ','),
           paste('"y0_lm":', coefficients['y0_lm'], ','),
           paste('"mumax":', coefficients['mumax'], ','),
           paste('"lag":',   coefficients['lag']),
           '}'
           ), f)
close(f)
