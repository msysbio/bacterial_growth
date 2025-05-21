library("growthrates")
library("jsonlite")

args <- commandArgs(TRUE)

input_csv         = 'input.csv'
input_json        = 'input.json'
coefficients_json = 'coefficients.json'
fit_json          = 'fit.json'

data   <- read.table(input_csv, header=T, sep=',')
config <- read_json(input_json)

model_fit <- fit_easylinear(data$time, data$value, h=config$pointCount)
coefficients = coef(model_fit)

f <- file(coefficients_json)
writeLines(toJSON(as.data.frame(coefficients), auto_unbox=T), f)
close(f)

f <- file(fit_json)
fit <- data.frame(r2=rsquared(model_fit), rss=deviance(model_fit))
writeLines(toJSON(fit, auto_unbox=T), f)
close(f)
