#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Shikhara Bhat
Email ID: shikharabhat@gmail.com
Date created: 2021-10-18 10:27:07
Date last modified: 2022-01-29 12:55:48
Purpose: This script sets up the model for parallelization across cores
(for reducing computation time). This simply allows us to run
simulations for various parameters in parallel by utilizing multiple
cores of the computing system simultaneously.
'''

import numpy as np
import multiprocessing as mp
import pandas as pd
from class_model import Model
from class_landscape import Landscape
from static_params import *

def combined_run(values,runs,N):

    '''
    This function runs the model for a given set of parameters and returns
    the mate counts for each of the strategies. We will loop over this function
    to scan the parameter space.
    
    values is a tuple of the form (freq,density,sex ratio).
    N is the number of individuals in the simulation.
    runs is the number of runs to average over while returning output.
    '''
    
    baffle_prop = values[0]    #Proportion of males that are bafflers
    dens = values[1]           #Population density (inds/sq m)
    ratio = values[2]          #Sex ratio
    area = N/dens              #Area of the grid. Set according to specified N and density
    side = np.sqrt(area)*100   #Side length of the grid in cm (the grid is a square)
    
    #create a landscape and fill it with bushes
    landscape = Landscape([0,side,5],[0,side,5])
    landscape.make_bushes(bush_dens,bush_size_mean,bush_size_sd)
    landscape.make_distance_list()
    
    #figure out how many males and females to make
    N_sig =  min(N,round(ratio*N))
    N_rec = max(0,N - N_sig)

    results = np.zeros(shape=(runs,289)) #289 is the number of columns of the output file
                
    for run in range(runs):

        #create a model
        model = Model(N_sig,N_rec,landscape)

        #fill it with males and females
        model.gen_callers(baffle_prop,SPL,side)

        #draw female velociteis from a lognormal dist
        fem_vel = np.random.lognormal(fem_vel_mean,fem_vel_sd,size=N_rec)

        #decompose into orthogonal components
        fem_vel /= np.sqrt(2)

        model.gen_receivers(fem_vel,fem_vel,side)

        #Run for one night
        model.run(night_dur,side)

        #extract results
        model_out = model.get_mate_counts(baffle_prop)

        run_results = [baffle_prop,dens,ratio,area]
        for param in model_out:
            for val in model_out[param]:
                run_results.append(val)


        results[run] = run_results

    return results

def simulate_and_save(params,runs,N,cores,save_path,filename):

    '''
    This function runs the previous function (combined_run) in parallel for a specified
    region in parameter space. runs represents how many runs to average over.
    '''
    
    #run the combined_run in parallel over specified number of cores
    '''
#    pool = mp.Pool(cores)
#    results = [pool.apply(combined_run, args=(values, runs,N)) for values in params]
#    pool.close()
    '''
    #format the output so that it looks nicer
#    results= []
#   for values in params:
    results = [combined_run(values, runs,N) for values in params]

    result_array = np.vstack(results)
    data_final= pd.DataFrame(result_array)
    
    colnames = ['baffle_prop','density','prop_males','area(m^2)']

    for stat_type in ['mean','sd','kurtosis','skew','min','max','median']:
        for out_type in ['baffle_success','caller_success','silent_success','total_male_success','total_female_success',
        'baffle_call_effort','baffle_within_bush_steps','baffle_within_bush_distance','baffle_across_bush_steps','baffle_across_bush_distance', 'baffle_total_steps','baffle_total_distance',
        'caller_call_effort','caller_within_bush_steps','caller_within_bush_distance','caller_across_bush_steps','caller_across_bush_distance', 'caller_total_steps','caller_total_distance',
        'silent_call_effort','silent_within_bush_steps','silent_within_bush_distance','silent_across_bush_steps','silent_across_bush_distance', 'silent_total_steps','silent_total_distance',
        'female_within_bush_random_steps','female_within_bush_random_distance',
        'female_across_bush_random_steps','female_across_bush_random_distance',
        'female_within_bush_phonotaxis_steps','female_within_bush_phonotaxis_distance',
        'female_across_bush_phonotaxis_steps','female_across_bush_phonotaxis_distance',
        'female_within_bush_total_steps','female_within_bush_total_distance',
        'female_across_bush_total_steps','female_across_bush_total_distance',
        'female_total_steps','female_total_distance']:
            
            
            colnames.append(str(out_type+"_"+stat_type))

    for ind_type in ['baffle','caller','silent','total_male','total_female']:
        colnames.append(str(ind_type+'_'+'proportion_mated'))
    
    data_final.columns = colnames
    #save to file
    data_final.to_csv(save_path+"output_"+str(N)+"_individuals_" + "array_"+str(filename)+".csv")
        
