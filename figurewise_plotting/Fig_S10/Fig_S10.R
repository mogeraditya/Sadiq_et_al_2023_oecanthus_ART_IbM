library(tidyverse)
library (ggplot2)
library(viridis)
library(greekLetters)

#Fig_S10_left panel

df <- read.csv('main_dataset.csv')

df <- filter (df, density==0.5 ,bush_density==1)   # population density = 0.5, bush_density==1 (structured habitat)

df$bush_density <- as.factor(df$bush_density)

df$density <- as.factor(df$density)


ggplot(df, aes(x=baffle_prop, y=mean_success, col=tactic)) + 
  geom_point(show.legend = F,size=4) + 
  labs(x='Proportion of bafflers', y='Mating success') +  
  geom_errorbar(data=df, aes(ymin=mean_success-ci, ymax=mean_success+ci),alpha=1,lwd= 1.5,show.legend = FALSE) +
  ylim(0, 0.5) + 
  theme(plot.title = element_text(size=20,hjust=1)) +
  scale_color_manual(values = c("#0072b2","#d55e00", "#39FF14")) +
  theme_classic(base_size=39) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 


#Fig_S10_middle panel

dat <- read.csv('bushdens_1.0_male_within_bush_prob_0.5.csv')

ggplot(dat, aes(x=baffle_prop, y=mean_success, col=tactic)) + 
  geom_point(show.legend = FALSE,size=4) + 
  labs(x='Proportion of bafflers', y='Mating success') +  
  geom_errorbar(data=dat, aes(ymin=mean_success-ci, ymax=mean_success+ci),alpha=1,lwd= 1.5,show.legend = FALSE) +
  ylim(0, 0.5) + 
  theme(plot.title = element_text(size=20,hjust=1)) +
  scale_color_manual(values = c("#0072b2","#d55e00", "#39FF14")) +
  theme_classic(base_size=39) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 


#Fig_S10_right panel

dat <- read.csv('bushdens_1.0_male_within_bush_prob_0.9.csv')


ggplot(dat, aes(x=baffle_prop, y=mean_success, col=tactic)) + 
  geom_point(show.legend = FALSE,size=4) + 
  labs(x='Proportion of bafflers', y='Mating success') +  
  geom_errorbar(data=dat, aes(ymin=mean_success-ci, ymax=mean_success+ci),alpha=1,lwd= 1.5,show.legend = FALSE) +
  ylim(0, 0.5) + 
  theme(plot.title = element_text(size=20,hjust=1)) +
  scale_color_manual(values = c("#0072b2","#d55e00", "#39FF14")) +
  theme_classic(base_size=39) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 
