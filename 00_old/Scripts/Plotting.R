setwd('bacterialGrowth_thesis/Data/experiments/RI/RI_batch_mucin2/RI_batch_mucin2_1/')

data <- read.table('growth_data.txt', header=T)

plot(data)

setwd('~/bacterialGrowth_thesis/DataParsed')
data <- read.table('RI_batch_mucin2_1.txt', header=T)

plot(data$time, data$liquidtotalcount)
title('liquid total count')


plot(data$time, data$liquidtotalcount)

x <- data$time
y1 <- data$liquidtotalcount
y2 <- data$liquidactivecount
y3 <- data$attachedactivecount

y <- data$OD

par(mfrow=c(2,1))

plot(x, y, ylab="OpticalDensity600nm", xlab="time(hours)")
title('Bacterial growth: RI_batch_mucin2_1')

plot(x,y1,type="l",col="blue", ylab="cell count per ul", xlab="time(hours)")
lines(x,y2,col="red")
lines(x,y3,col="green")

metabolites <- colnames(data)[!colnames(data) %in% c("time","OD","pH","liquidtotalcount","liquidactivecount","attachedtotalcount")]
metabolites_data <- data[, c("time",metabolites)]
# plotcolors <- c("red","orange", "gold","yellow","light green","dark green","cyan","light blue",
#                 "dark blue", "light purple", "dark purple","gray","black")

plotcolors <- brewer.pal(12,'Paired')

par(mfrow=c(1,1))
for (i in c(2:length(metabolites_data))) {
  if(i == 2) {
    plot(metabolites_data$time, metabolites_data[,i], type="l", col=plotcolors[i])
  } else {
    lines(metabolites_data$time, metabolites_data[,i], ylim = c(0:10), col=plotcolors[i])
  }
}