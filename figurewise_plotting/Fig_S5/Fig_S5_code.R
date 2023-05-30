library (ggplot2)
library (tidyverse)
library(viridis)
library(greekLetters)


dat <- read.csv('female_movement.csv')
dat$random_prop <- dat$mean_random_steps/dat$mean_total_steps
densities <- unique (dat$density)


dat$bush_density <- ifelse(dat$bush_density==0,'Homogenous',dat$bush_density)
dat$bush_density <- ifelse(dat$bush_density==0.5,paste (greeks('rho'),' = 0.5',sep=''),dat$bush_density)
dat$bush_density <- ifelse(dat$bush_density==1,paste (greeks('rho'),' = 1',sep=''),dat$bush_density)
dat$bush_density <- ifelse(dat$bush_density==1.5,paste (greeks('rho'),' = 1.5',sep=''),dat$bush_density)
dat$bush_density <- ifelse(dat$bush_density==2,paste (greeks('rho'),' = 2',sep=''),dat$bush_density)
dat$bush_density <- as.factor(dat$bush_density)

  
df <- filter (dat,density==0.05)  #Enter required value of population density (i.e., 0.05, 0.25,05,0.75,1)

ggplot(df, aes(x=baffle_prop, y=random_prop, group=bush_density, color=bush_density)) + 
  geom_point(show.legend = T,size=5) + 
  labs(x='Proportion of bafflers',y='Random movement propensity') +
  annotate("text",  x=Inf, y = Inf, label = expression(paste(italic(d),' = 0.05')), vjust=1, hjust=1,size=12,fontface =2) + #Enter the appropriate value of population density in the quotes of the paste function.
  theme(plot.title = element_text(size=20,hjust=1)) +
  ylim(0,1) +
  scale_color_discrete(name="") +
  theme_classic(22.5) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold') )

  
  
 