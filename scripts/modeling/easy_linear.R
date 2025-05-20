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
writeLines(c(
           '{',
           paste('"y0":',    coefficients['y0'], ','),
           paste('"y0_lm":', coefficients['y0_lm'], ','),
           paste('"mumax":', coefficients['mumax'], ','),
           paste('"lag":',   coefficients['lag']),
           '}'
           ), f)
close(f)

f <- file(fit_json)
writeLines(c(
           '{',
           paste('"r2":',  rsquared(model_fit), ','),
           paste('"rss":', deviance(model_fit)),
           '}'
           ), f)
close(f)
