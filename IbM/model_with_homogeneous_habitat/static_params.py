#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Shikhara Bhat
Email ID: shikharabhat@gmail.com
Date created: 2021-10-18 10:48:59
Date last modified: 2022-03-15 13:48:40
Purpose: This script contains all the static
parameters that are held constant in every run of
the simulation. Source for the parameters (if any)
is specified here through comments.
'''

import numpy as np

'''Amplitude parameters'''
#Loudness of callers will be drawn from a Normal(SPL,SPL_sd) dstribution
SPL = 60.8 #Mean Loudness of the signaller at source (in dB SPL, from Rittik's thesis, fig 4.9)
SPL_sd = 3.6 #SD of the loudness (from Rittik's thesis, fig 4.9)

'''Baffling related parameters'''
baffle_advantage_mean = 10.1 #Mean increase in loudness (in dB SPL) due to using a baffle (From Rittik's thesis, fig 4.9)
baffle_advantage_SD = 1.3 #SD of the increase in loudness (in dB SPL) due to using a baffle (From Rittik's thesis, fig 4.9)

'''Phonotaxis related parameters'''
threshold_SPL = 45 #Minimum loudness (in dB SPL) that is detectable by a receiver (Eyeballed from Rittik's thesis, fig 3.5)
min_SPL_for_movement = 60 #Min loudness (in dB SPL) that guarantees that a female exhibits phonotaxis towards source (Eyeballed from Rittik's thesis, fig 3.5)
threshold_SPL_diff = 3 #Min difference in loudness (in dB SPL) b/w two sources that is required for a female to exhibit a preference. Sourced from Sambita's thesis.

'''Timescales'''
night_dur = 72 #how many timesteps constitute one night
decision_dur = night_dur #How often a cricket decides whether it should start calling or not (once a night, rn)
mating_duration = 6 #mating duration is the duration of mating + refractory period.
#assuming a night is 8 hours long, the value of mating duration above is equal to 30 mins in real time.
#This is close to the mean of the mating duration of a large and small male used in Rittik's paper, i.e., 15 and 42 mins. 

'''Movement-related parameters'''

#Within bush movement velocity parameters in cm/s (From Aamir's data)

#female mean and sigma (will be put into lognormal dist)
fem_vel_mean = 2.95
fem_vel_sd = 1.03

#male mean and sigma (will be put into lognormal dist)
male_vel_mean = 2.59
male_vel_sd = 0.88

#Across bush movement propensities (will be put into lognormal dist)
fem_dist_mean = 2.1
fem_dist_sd = 0.82

male_dist_mean = 1.93
male_dist_sd = 0.75

mating_dist = 5 #distance b/w a signaller and a receiver which counts as a mating (in cm) (Aamir, personal observations)

#MOVEMENT PROPENSITIES
#Mean across-bush movement propensity (from Viraj's data, hi predation treatment not considered)
fem_mov_prop_across_bush = 0.1598 #From data (female_movement_propensity_and_total_distance.csv)
male_mov_prop_across_bush = 0.1197 #From data (male_movement_propensity.csv)
mated_phonotaxis_prop = 0.35 #To get from Sambita's thesis

#Mean within-bush movement propensity (from Aamir's data)
fem_mov_prop_within_bush = 0.8
male_mov_prop_within_bush = 0.35

'''Call effort related parameters'''
#Mean calling propensity of signallers - decides caller : silent ratio
male_call_prop = 0.5 #From data (male_movement_propensity.csv), the value is actually 0.5543
#Call effort of signallers (how often they call in a given night), from data
#Samples will be drawn from a truncated normal dist (truncated to be in (0,1])
effort_mean = 0.5
effort_sd = 0.26
#call_effort = np.array(data['calling_effort'].dropna())

'''Spatial organization (bush-related) parameters'''
#threshold distance of centers (in cm) past which two bushes can be considered completely
#independent of each other in terms of signal propagation
threshold_bush_dist = 1000 #Arbitrary choice of 10m for now (seems conservative)

#bush size parameters (in cm). Size is drawn from a half-Normal distribution of specified size
#I've put in dummy values for now
bush_size_mean = 81.21 #From Viraj cage data (check master_datasheet.csv)
bush_size_sd = 36.40 #From Viraj cage data (check master_datasheet.csv)

#bush density (bushes/sq m)
bush_dens = 1.625     #(from Viraj's outdoor cage experiment data)