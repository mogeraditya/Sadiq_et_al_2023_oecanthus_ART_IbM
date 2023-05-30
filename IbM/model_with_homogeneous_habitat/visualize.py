#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Shikhara Bhat
Email ID: shikharabhat@gmail.com
Date created: 2021-10-18 10:24:39
Date last modified: 2022-01-06 15:45:25
Purpose: This script is used to visualize the
simulation, just to get a visual idea of what is
going on. This is NOT necessary for the final output.
'''
from class_model import Model
from class_landscape import Landscape
from class_bush import Bush
from static_params import *

np.random.seed(5)

N = 20 #Total number of individuals
#dens = 1 #Population density (in inds/sq m)
#side = ((N/dens)**0.5)*100 #times 100 to convert from m to cm
side = 1000
landscape = Landscape([0,side,5],[0,side,5])
landscape.make_bushes(0.5,bush_size_mean,bush_size_sd)
#bush1 = Bush(100,200,100)
#bush2 = Bush(300,200,100)

#landscape.bushlist = [bush1,bush2]
#landscape.bushcenters = [(100,200),(300,200)]
landscape.make_distance_list()
sim = Model(int(round(0.5*N)),int(round(0.5*N)),landscape) #sex ratio is 1:1
sim.gen_callers(0.2,SPL,side) #baffle_prop is 0.2

#draw female velocities from a lognormal dist
fem_vel = np.random.lognormal(fem_vel_mean,fem_vel_sd,size=int(round(0.5*N)))

#decompose into orthogonal components
fem_vel /= np.sqrt(2)

sim.gen_receivers(fem_vel,fem_vel,side)

#directory to which to save the visualization
save_dir = ''

sim.run(10,side)
sim.visualize(1,save=True, filename = (save_dir+str('fig_1_A.png')))


#Directory in which to store the images
#directory = '/mnt/data/Work/summer_and_semester_projects/2021_Balakrishnan_simulations/git_repo/baffled_crickets/visualization/test_02_no_bushes/'
#sim.run(2*night_dur,side,True,directory)
