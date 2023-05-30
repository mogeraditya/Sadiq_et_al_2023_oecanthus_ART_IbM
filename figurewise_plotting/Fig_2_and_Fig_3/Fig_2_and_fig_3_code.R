library(tidyverse)
library (ggplot2)
library(viridis)
library(greekLetters)


#Figure 2A and 2b

df <- read.csv('main_dataset.csv')

df <- filter (df, density!=0.01 & density!=0.10 ,bush_density==1)   # enter required bush density  (i.e., 0 (for homogenous), 0.5, 1, 1,5, 2

df$bush_density <- ifelse(df$bush_density==0,'Homogenous',df$bush_density)
df$bush_density <- as.factor(df$bush_density)

df$density <- as.factor(df$density)

dat <- filter (df,density== 0.05) #enter required value of population density here (i.e., 0.05,0.25,0.5,0.75,1)

g <-ggplot(dat, aes(x=baffle_prop, y=mean_success, col=tactic)) + 
  geom_point(show.legend = F,size=4) + 
  labs(x='Proportion of bafflers', y='Mating success') +  
  geom_errorbar(data=dat, aes(ymin=mean_success-ci, ymax=mean_success+ci),alpha=1,lwd= 1.5,show.legend = FALSE) +
  ylim(0, 1.65) +  
  annotate("text",  x=Inf, y = Inf, label = expression(paste(italic(d),' = 0.05')), vjust=1, hjust=1,size=12,fontface = 2) + #enter the required value of population density (d) to be printed on the plot
  theme(plot.title = element_text(size=20,hjust=1)) +
  scale_color_manual(values = c("#0072b2","#d55e00", "#39FF14")) +
  theme_classic(base_size=39) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 
g


####################################################################################################################


#Fig 2B and 2C

df <- read.csv('main_dataset.csv')

df <- filter (df, density!=0.01 & density!=0.1,tactic=='baffler',bush_density!=1.625)

bush_dens <- unique (df$bush_density)


result <- data.frame()

for (i in bush_dens) {
  dat <- filter(df,bush_density==i)
  linmod <- lm(mean_success ~  baffle_prop*density, data= dat)  # linear regression analaysis of the effect of proportion of bafflers, population density and their interaction on the mating success of bafflers
  mod_vals <- data.frame (bush_dens= i,frequency_effect = summary(linmod)$coefficients[2,1], p_value = summary(linmod)$coefficients[2,4],lower_ci = confint(linmod)[2,1], upper_ci = confint(linmod)[2,2], density = summary(linmod)$coefficients[3,1], p_value = summary(linmod)$coefficients[3,4],lower_ci = confint(linmod)[3,1], upper_ci = confint(linmod)[3,2], density_frequency = summary(linmod)$coefficients[4,1], p_value=summary(linmod)$coefficients[4,4],lower_ci = confint(linmod)[4,1], upper_ci = confint(linmod)[4,2], r_squared = summary(linmod)$adj.r.squared)
  result <- rbind (result, mod_vals)   #extracting the coefficients f the predictors in the regression analysis
  
}

write.csv(result,'linearmodel_baffler_fitness.csv',row.names = FALSE)  #wrtitng out the reuslts of the regression analaysis into a CSV file


ggplot(result, aes(x = as.factor(bush_dens), y = frequency_effect)) +
  geom_point(size=5,col='black') +
  scale_x_discrete(labels=c('Homo\ngenous', paste(greeks('rho'),'=0.5', sep =""), paste(greeks('rho'),'=1', sep =""),paste(greeks('rho'),'=1.5', sep =""),paste(greeks('rho'),'=2', sep =""))) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci), color='black',size=2) +
  theme(legend.position="none") +
  xlab('') + 
  ylab ('Effect of proportion of \nbafflers') +
  theme_classic(32) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 


ggplot(result, aes(x = as.factor(bush_dens), y = density_frequency,group=1)) +
  geom_point(size=5,col='black') +
  scale_x_discrete(labels=c('Homo\ngenous', paste(greeks('rho'),'=0.5', sep =""), paste(greeks('rho'),'=1', sep =""),paste(greeks('rho'),'=1.5', sep =""),paste(greeks('rho'),'=2', sep =""))) +
  geom_errorbar(aes(ymin = lower_ci.2, ymax = upper_ci.2), color='black',size=2) +
  theme(legend.position="none") +
  xlab ('') +
  ylab ('Proportion of bafflers \nx\nPopulation density') +
  theme_classic(32) +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 


################################################################################################################33

#Fig_3

df <- read.csv('main_dataset.csv')

df <- filter (df, density!=0.01 & density!=0.1 & bush_density!=1.625)

bush_dens <- unique (df$bush_density)

pop_dens <- unique (df$density)

result <- data.frame()


for (i in bush_dens){
  for (j in pop_dens) {
    dat <- filter (df,bush_density==i,density==j)
    linmod <- lm(mean_success ~ tactic + baffle_prop, data= dat)  #linear regression analysis of the effect of the ART and proportion of bafflers on the mating success
    mod_vals <- data.frame (bush_dens= i, pop_density= j,baffler_success = summary(linmod)$coefficients[1,1], p_value = summary(linmod)$coefficients[1,4], caller_success_diff = summary(linmod)$coefficients[2,1], p_value = summary(linmod)$coefficients[2,4], silent_success_diff = summary(linmod)$coefficients[3,1], p_value=summary(linmod)$coefficients[3,4], frequency_effect = summary(linmod)$coefficients[4,1], p_value = summary(linmod)$coefficients[4,4],r_squared = summary(linmod)$adj.r.squared)
    result <- rbind (result, mod_vals)
    
  }   #extracting the coefficients f the predictors in the regression analysis

}    

write.csv(result,'linearmodel_tactic_fitness.csv',row.names = FALSE)  #writing out the results of the regression analysis into a CSV file

ggplot(result, aes(x = as.factor(pop_density), y = as.factor(bush_dens), fill = caller_success_diff)) +
  geom_tile(color = "black") +
  geom_text(aes(label = as.character(round(baffler_success,3))), color = "red",fontface = "bold", size = 5) +
  scale_y_discrete(labels=c('Homogenous', paste(greeks('rho'),' = 0.5', sep =""), paste(greeks('rho'),' = 1', sep =""),paste(greeks('rho'),' = 1.5', sep =""),paste(greeks('rho'),' = 2', sep =""))) +
  scale_fill_viridis_c() +
  xlab(expression (paste('Population density (',italic('d'),')'))) + 
  ylab ('') +
  labs(fill='Difference\nin mating\nsuccess \n(Caller - Baffler)') +
  theme(text = element_text(size = 22, face="bold"))  




ggplot(result, aes(x = as.factor(pop_density), y = as.factor(bush_dens), fill = silent_success_diff)) +
  geom_tile(color = "black") +
  geom_text(aes(label = as.character(round(baffler_success,3))), color = "red",fontface = "bold", size = 5) +
  scale_y_discrete(labels=c('Homogenous', paste(greeks('rho'),' = 0.5', sep =""), paste(greeks('rho'),' = 1', sep =""),paste(greeks('rho'),' = 1.5', sep =""),paste(greeks('rho'),' = 2', sep =""))) +
  scale_fill_viridis_c() +
  xlab(expression (paste('Population density (',italic('d'),')'))) + 
  ylab ('') +
  labs(fill='Difference\nin mating\nsuccess \n(Silent - Baffler)') +
  theme(text = element_text(size = 22, face="bold"))  +
  theme(axis.text=element_text(face='bold'),axis.title = element_text(face='bold')) 
 



