library("growthrates")
library("jsonlite")

args <- commandArgs(TRUE)

input_csv         = 'input.csv'
coefficients_json = 'coefficients.json'
fit_json          = 'fit.json'

data <- read.table(input_csv, header=T, sep=',')

## Initial parameter estimation from spline fit
spline_fit <- fit_spline(data$time, data$value)
summary(spline_fit)
spline_coefficients <- coef(spline_fit)

y0_est    = spline_coefficients['y0']
mumax_est = spline_coefficients['mumax']
names(y0_est)    <- NULL
names(mumax_est) <- NULL

max_value = max(data$value)

p     <- c(y0 = y0_est, mumax = mumax_est, K = max_value)
lower <- c(y0 = 1e-9,   mumax = 0,         K = 0)

model_fit <- fit_growthmodel(FUN       = grow_logistic,
                             transform = 'log',
                             time      = data$time,
                             y         = data$value,
                             p         = p,
                             lower     = lower)

print("## SUMMARY START")
summary(model_fit)
print("## SUMMARY END")

coefficients = coef(model_fit)

f <- file(coefficients_json)
writeLines(toJSON(as.data.frame(coefficients), auto_unbox=T), f)
close(f)

f <- file(fit_json)
fit <- data.frame(r2=rsquared(model_fit), rss=deviance(model_fit))
writeLines(toJSON(fit, auto_unbox=T), f)
close(f)
