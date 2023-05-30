library(tidyverse)
library (ggplot2)
library(viridis)
library(greekLetters)


#Fig_2A (Without male movement)

df <- read.csv('homogenous_no_male_movement.csv')

df <- filter (df,density==0.5)  #Population density equal to 0.5

g <-ggplot(df, aes(x=baffle_prop, y=mean_success, col=tactic)) + 
  geom_point(show.legend = FALSE,size=4) + 
  labs(x='Proportion of bafflers', y='Mating success') +  
  geom_errorbar(data=df, aes(ymin=mean_success-ci, ymax=mean_success+ci),alpha=1,lwd= 1.5,show.legend = FALSE) +
  ylim(0, 1.25) +  
  theme(plot.title = element_text(size=20,hjust=1)) +
  scale_color_manual(values = c("#0072b2","#d55e00", "#39FF14")) +
  theme_classic(base_size=39) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 
g



#Fig_2B  (With caller and silent male movement)

df <- read.csv('main_dataset.csv')  

df <- filter (df, density!=0.01 & density!=0.10 ,bush_density==0)   # Bush density = 0 (i.e., denotes homogenous habitat)

df$bush_density <- ifelse(df$bush_density==0,'Homogenous',df$bush_density)
df$bush_density <- as.factor(df$bush_density)

df$density <- as.factor(df$density)

dat <- filter (df,density== 0.05) #Population density equal to 0.5

g <-ggplot(dat, aes(x=baffle_prop, y=mean_success, col=tactic)) + 
  geom_point(show.legend = F,size=4) + 
  labs(x='Proportion of bafflers', y='Mating success') +  
  geom_errorbar(data=dat, aes(ymin=mean_success-ci, ymax=mean_success+ci),alpha=1,lwd= 1.5,show.legend = FALSE) +
  ylim(0, 1.25) +  
  theme(plot.title = element_text(size=20,hjust=1)) +
  scale_color_manual(values = c("#0072b2","#d55e00", "#39FF14")) +
  theme_classic(base_size=39) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 
g


