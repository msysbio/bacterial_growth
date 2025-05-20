library("growthrates")
library("jsonlite")

args <- commandArgs(TRUE)

input_csv         = args[1]
coefficients_json = 'coefficients.json'
fit_json          = 'fit.json'

data <- read.table(input_csv, header=T, sep=',')

## initial parameters and box constraints
max_value = max(data$value)

p     <- c(y0 = 0.01,  mumax = .1,   K = max_value,      h0 = 1)
lower <- c(y0 = 0.001, mumax = 1e-2, K = max_value / 10, h0 = -10)
upper <- c(y0 = 0.1,   mumax = 4,    K = max_value * 10, h0 = 10)

model_fit <- fit_growthmodel(FUN       = grow_baranyi,
                             transform = 'log',
                             time      = data$time,
                             y         = data$value,
                             p         = p,
                             upper     = upper,
                             lower     = lower)

# Evaluate summary to ensure an error is raised if there are fit issues:
summary(model_fit)

coefficients = coef(model_fit)

# TODO: try toJSON(as.data.frame(coefficients))

f <- file(coefficients_json)
writeLines(c(
           '{',
           paste('"y0":',    coefficients['y0'], ','),
           paste('"mumax":', coefficients['mumax'], ','),
           paste('"K":',     coefficients['K'], ','),
           paste('"h0":',    coefficients['h0']),
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
