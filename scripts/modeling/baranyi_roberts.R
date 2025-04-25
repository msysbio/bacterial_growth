library("growthrates")
library("jsonlite")

args <- commandArgs(TRUE)

input_csv   = args[1]
output_json = args[2]

data <- read.table(input_csv, header=T, sep=',')

## initial parameters and box constraints
p <- c(y0 = 0.03, mumax = .1, K = 0.1, h0 = 1)

model_fit <- fit_growthmodel(FUN  = grow_baranyi,
                             time = data$time,
                             y    = data$value,
                             p    = p)

coefficients = coef(model_fit)

f <- file(output_json)
writeLines(c(
           '{',
           paste('"y0":',    coefficients['y0'], ','),
           paste('"mumax":', coefficients['mumax'], ','),
           paste('"K":',     coefficients['K'], ','),
           paste('"h0":',    coefficients['h0']),
           '}'
           ), f)
close(f)
