library(tidyverse)
library (ggplot2)
library(viridis)
library(greekLetters)



dat<-read.csv('silent_males_females_only.csv')

dat <- filter (dat, density!=0.1,density!=0.01,bush_density!=1.625)

dat$bush_density <- ifelse(dat$bush_density==0,'Homogenous',dat$bush_density)
dat$bush_density <- ifelse(dat$bush_density==0.5,paste (greeks('rho'),' = 0.5',sep=''),dat$bush_density)
dat$bush_density <- ifelse(dat$bush_density==1,paste (greeks('rho'),' = 1',sep=''),dat$bush_density)
dat$bush_density <- ifelse(dat$bush_density==1.5,paste (greeks('rho'),' = 1.5',sep=''),dat$bush_density)
dat$bush_density <- ifelse(dat$bush_density==2,paste (greeks('rho'),' = 2',sep=''),dat$bush_density)
dat$bush_density <- as.factor(dat$bush_density)



ggplot(dat, aes(x=density, y=mean_silent_success, group=bush_density, color=bush_density)) + 
  geom_point(show.legend = F,size=4) + #change value of show.legend to T to plot the legends
  labs(x='Population density', y='Mating success') +
  geom_errorbar(data=dat, aes(ymin=mean_silent_success-ci_silent_success, ymax=mean_silent_success+ci_silent_success),alph=1,show.legend = F ) +
  theme(plot.title = element_text(size=20,hjust=1)) +
  scale_x_continuous(breaks=c(0,0.25,0.5,0.75,1)) +
  scale_color_discrete(name="") +
  theme_classic(base_size=39) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold') )
