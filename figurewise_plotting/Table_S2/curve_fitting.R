############################
#Fit distributions to empirically observed data about O. henryi (experiments
#by M.A. Sadiq (unpublished) and Torsekar and Balakrishnan , 2020) to find the parameters for the most likely distributions (using MLE
#and AIC)
#Written by Mohammed Aamir Sadiq
#Slightly modified by Shikhara Bhat
#CES, IISc, India
#Date: Thu Jan  6 14:43:59 2022
###########################

library (fitdistrplus)
library (MASS)

dat <- read.csv ('dataset_for_curve_fitting.csv')

curvefitting <- function (data,ftype){
  mydata <- data[!is.na(data)]
  fit <- fitdist(mydata,ftype,method='mle')
  statistics <- gofstat (fit)
  print (paste('observed ks distance = ',statistics$ks))
  print (paste('ks disatnce (for alpha = 0.05) =',1.36/sqrt(length(mydata))))  #if ks distance (see gofstat summary in previous command) is less than d_signigicance, the distributions are similar at 5% confidence level.
  plot (fit)
 
  
  return (fit)
}

##1) The following are the best distributions for the variables chosen from the list = (norm, lnorm, exp, pois, cauchy, gamma, logis, nbinom, geom, beta, weibull). 
##2)The distribution whose observed ks (Kolmogorov-Smirnov) distance was less than the critical ks distance (i.e., for alpha = 0.05). Fomr more information, see gofstat summary.
##3) Lowest AIC value may not reflect lowest ks distance.

#Parameter estimation (using MLE)

f_within_bush_dist <- curvefitting(dat$f_dist_interbush,'lnorm')
m_within_bush_dist <- curvefitting(dat$m_dist_interbush,'lnorm')
f_acrossbush_dist <- curvefitting(dat$f_dist_within_bush,'lnorm')
m_acrossbush_dist<- curvefitting(dat$m_dist_within_bush,'lnorm')
calling_effort <- curvefitting(dat$calling_effort,'norm')
bush_width <- curvefitting(dat$bush_width,'norm')


#Below are the MLE parameters. The notation is (mean,sd)
# DONE indicates that this has been implemented in the main Python code
#m_dist : lnorm(1.93,0.75)  --- DONE
#f_dist : lnorm(2.1,0.82) --- DONE
#male_vel : lnorm(2.59,0.88) --- DONE
#female_vel :  lnorm(2.95,1.03) --- DONE
#calling_effort : norm(0.5,0.26) --- DONE
#bush_width : norm(81.21,35.40) --- DONE






