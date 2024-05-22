#RStudio recommended

#Load require libraries
library(reshape2)
library(ggplot2)
library(magrittr)
library(dplyr)

# Plot Figure 4

#RFX-BMS results for ToM models, sorted as ToM-0, -1, -2, -3, -4, -5, random model
#tom_rfxbms <- c(0.3121083538029856, 0.25681556251760923, 0.033771758226165474, 0.1796562349817207, 0.1796562349817207, 0.037991855489798325)  # Empty = nK
#tom_rfxbms <- c(0.04438808607349401, 0.060042082060623995, 0.03998480910561234, 0.5150285213571848, 0.021108312931286323, 0.060042082060623995, 0.056432653696174825, 0.060042082060623995, 0.056432653696174825, 0.060042082060623995, 0.026456634897576842)
tom_rfxbms <- c(0.6332791717155488, 0.03430716484602665, 0.03817927000560224, 0.09685565984229404, 0.09685565984229404, 0.1005230737482341)

names = c("Epistemic","Cut-1","ToM-2","ToM-3","ToM-4","Random") #Model names
#names = c("Epistemic T", "Epistemic F", "Cut-1 lr T", "Cut-1 lr F", "Cut-1 rl T", "Cut-1 rl F", 
#          "Cut-2 lr T", "Cut-2 lr F", "Cut-2 rl T", "Cut-2 rl F", "Random")
names <- factor(names, levels = names) #Turn into ordered factor so ggplot doesn't sort the bars
data <- data.frame(values=tom_rfxbms,names=names) #Convert to data frame

#Plot Figure 4
p <- ggplot(data=data, aes(x=names, y=values)) +
  geom_bar(stat="identity") +
  scale_y_continuous(limits = c(0, 0.7), breaks = c(0, 0.1, 0.2, 0.3, 0.4, 0.5)) + 
  labs(x="",y="") + geom_text(data=data,aes(x=names,y=values,label=format(round(values, digits=3),nsmall = 3)),
                                                                    vjust=-1,size=6.5) +
  xlab("Model") + ylab("Proportion of population fitted")  +
  theme(legend.title=element_blank(), 
      axis.text.x = element_text(size=20, angle=90),
      axis.text.y = element_text(size=20),
      axis.title.x = element_text(size=20),
      axis.title.y = element_text(size=20),
      legend.text = element_text(size=18))

#Show Figure 4
p

# Plot Figure 5

#Set working directory to plotcode.R file location (requires RStudio - without RStudio please set working directory to location of correctrates_usecedegaoFalse.csv manually)
setwd(substr(rstudioapi::getSourceEditorContext()$path,1,nchar(rstudioapi::getSourceEditorContext()$path)-11))
data <- read.csv2('correct_rates.csv', header=FALSE)  #Read coherence data, change to 'usecedegaoTrue' to investigate Cedegao's coherence

#Read coherence for all participants, convert to numeric, and remove NA values
tomall<-as.list(strsplit(data[nrow(data),], ",")[[1]])
tomall <- as.numeric(tomall)
tomall <- tomall[!is.na(tomall)]

#Read coherence for participants where random model fits best, convert to numeric, and remove NA values
tomrand<-as.list(strsplit(data[nrow(data)-1,], ",")[[1]])
tomrand <- as.numeric(tomrand)
tomrand <- tomrand[!is.na(tomrand)]

data3 <- cbind(tomall) # Convert to column
data3 <- as.data.frame(unlist(data3[,1])) #Convert to data frame
rownames(data3) <- c() # Remove row names
colnames(data3)<- c() # Remove column names

names(data3) <- "data3" # Name only column `data3' so we can refer to it

# Mark outliers
data3 <- data3 %>% 
  mutate(outlier = data3 > median(data3) + 
           IQR(data3)*1.5 | data3 < median(data3) -
           IQR(data3)*1.5) 

# List of outliers where random model fits best
randdata <- data.frame(data3=tomrand,
                       outlier=TRUE)

data_norand <- data3[which(!(data3$data3 %in% tomrand)),]  # Data without participants where random model fits best
data_norand <- data_norand[which(data_norand$outlier == TRUE),]  # Outliers where ToM model fits best

length(data3[which(data3$data3 > 0.736),][,1])  # How many participants have a coherence > 0.736 ?
49 - length(data3[which(data3$data3 > 0.5),][,1])  # How many participants have a coherence > 0.5 ?

# Create Figure 5
data3 %>% 
  ggplot(aes("",data3),ylim=c(0,1),xlab="",xtitle="",ylab="",) + 
  geom_boxplot(outlier.shape = NA) + coord_cartesian(ylim = c(0, 1)) +
  geom_point(data = data_norand,#function(x) dplyr::filter(x, outlier), 
             position = "jitter") + geom_point(shape=4,data=randdata,position = "jitter") + 
  coord_flip() + scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, 0.25)) + 
  theme(
    axis.text.y=element_blank(),  #remove y axis labels
    axis.ticks.y=element_blank(),  #remove y axis ticks
    axis.text=element_text(size=12),
    axis.title.x=element_blank(),
    axis.title.y=element_blank()
  )

# Calculate mean, median, and IQR for coherence
round(mean(data3[,1]),digits=3)
round(median(data3[,1]),digits=3)
round(IQR(data3[,1]),digits=3)
