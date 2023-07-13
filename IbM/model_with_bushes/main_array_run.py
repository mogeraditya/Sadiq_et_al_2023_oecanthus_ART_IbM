#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Shikhara Bhat
Email ID: shikharabhat@gmail.com
Date created: 2022-01-15 18:26:30
Date last modified: 2022-01-16 16:30:36
Purpose: A spatial individual-based model (IbM) to simulate mating success of 
three alternative reproductive tactics (ARTs) in a species of Indian tree
cricket (Oecanthus henryi).

Males of O. henryi exhibit three distinct ARTs to attract females. Males may
either call from a location without any modification to their calls, use a 
leaf as an acoustic baffle to increase the amplitude of their calls, or stay
silent and not call.
The goal of this IbM is to examine the effects of three demographic factors -
baffling trait frequency, population density, and sex ratio - on the mating
success of these three alternative reprodictive tactics, and check for the
conditions under which robust coexistence of all three strategies is possible.

The code for this model is modularized for organizational ease. This script is 
the parallelized version of the 'main' script that brings it all together.


This main script is meant to be submitted as an array job in a HPC which allows us to parallelize over multiple nodes
'''
import argparse
from set_up_parallelization import simulate_and_save

################ Take arguments as input (for looping over in the array job) ################################

if __name__ == "__main__": 
     
     #the if condition makes sure that arguments are asked for only when this file is the main program
     #and not when it is imported in another piece of code
     #p

     parser = argparse.ArgumentParser(description="IbM of alternative reproductive tactics in tree crickets")

     parser.add_argument("-f", "--freq", dest="frequency", help="Baffling trait frequency", required=True)
     parser.add_argument("-d", "--dens", dest="density", help="Population density (inds/sq m)", required=True)
     parser.add_argument("-file","--filename",dest='file',help='unique index for the filename',required=True)

     args = parser.parse_args() 
     freq = float(args.frequency)
     dens = float(args.density)
     file = str(args.file)


#Location to which output should be stored
save_path = "D:/github/Sadiq_et_al_2023_oecanthus_ART_IbM/output/"

##################### Simulation parameters (for computing) ###################
runs = 2 #Number of realizations over which to average the results
cores = 1 #Number of cores to use while running the simulation
N = 500    #Number of individuals to use in the simulation

#Run the model
simulate_and_save([[freq,dens,0.5]],runs, N, cores, save_path, file)