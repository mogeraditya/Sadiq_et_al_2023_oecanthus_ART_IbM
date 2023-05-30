library(tidyverse)
library (ggplot2)
library(viridis)
library(greekLetters)

df <- read.csv('main_dataset.csv')

df <- filter (df, density!=0.01 & density!=0.10 ,bush_density==1)   # enter required bush density  (i.e., 0 (for homogenous), 0.5, 1, 2

df$bush_density <- ifelse(df$bush_density==0,'Homogenous',df$bush_density)
df$bush_density <- as.factor(df$bush_density)

df$density <- as.factor(df$density)




dat <- filter (df,density== 0.05) #enter required value of population density here (i.e., 0.05,0.25,0.5,0.75,1)

g <-ggplot(dat, aes(x=baffle_prop, y=mean_success, col=tactic)) + 
  geom_point(show.legend = F,size=4) + 
  labs(x='Proportion of bafflers', y='Mating success') +  
  geom_errorbar(data=dat, aes(ymin=mean_success-ci, ymax=mean_success+ci),alpha=1,lwd= 1.5,show.legend = FALSE) +
  ylim(0, 1.65) +  
  annotate("text",  x=Inf, y = Inf, label = expression(paste(rho,' = 2 ; ',italic(d),' = 0.05')), vjust=1, hjust=1,size=12,fontface = 2) + #enter the required value of the bush density (rho) and population density (d) to be printed on the plot
  theme(plot.title = element_text(size=20,hjust=1)) +
  scale_color_manual(values = c("#0072b2","#d55e00", "#39FF14")) +
  theme_classic(base_size=39) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 
g
