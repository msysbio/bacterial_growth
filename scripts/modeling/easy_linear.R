library("growthrates")
library("jsonlite")

args <- commandArgs(TRUE)

input_csv         = args[1]
coefficients_json = 'coefficients.json'
fit_json          = 'fit.json'

data <- read.table(input_csv, header=T, sep=',')

model_fit <- fit_easylinear(data$time, data$value)
coefficients = coef(model_fit)

f <- file(coefficients_json)
writeLines(toJSON(as.data.frame(coefficients)), f)
close(f)

f <- file(fit_json)
fit <- data.frame(r2=rsquared(model_fit), rss=deviance(model_fit))
writeLines(toJSON(fit), f)
close(f)
