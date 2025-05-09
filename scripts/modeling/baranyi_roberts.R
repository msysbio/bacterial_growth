library("growthrates")
library("jsonlite")

args <- commandArgs(TRUE)

input_csv   = args[1]
output_json = args[2]

data <- read.table(input_csv, header=T, sep=',')

## initial parameters and box constraints
max_value = max(data$value)

p     <- c(y0 = 0.03,  mumax = .1,   K = max_value,      h0 = 1)
lower <- c(y0 = 0.001, mumax = 1e-2, K = max_value / 10, h0 = -10)
upper <- c(y0 = 0.1,   mumax = 1,    K = max_value * 10, h0 = 10)

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

f <- file(output_json)

# TODO: try toJSON(as.data.frame(coefficients))
# TODO: Write model fit to file as well

writeLines(c(
           '{',
           paste('"y0":',    coefficients['y0'], ','),
           paste('"mumax":', coefficients['mumax'], ','),
           paste('"K":',     coefficients['K'], ','),
           paste('"h0":',    coefficients['h0']),
           '}'
           ), f)
close(f)
