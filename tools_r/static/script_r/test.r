# 1. Loading 
data("mtcars")
# Create my_data
my_data <- mtcars
# Open a pdf file
pdf("rplot.pdf") 
# 2. Create a plot
plot(x = my_data$wt, y = my_data$mpg,
     pch = 16, frame = FALSE,
     xlab = "wt", ylab = "mpg", col = "#2E9FDF")
# Close the pdf file
dev.off() 
