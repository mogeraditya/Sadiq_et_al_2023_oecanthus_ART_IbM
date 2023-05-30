#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Shikhara Bhat
Email ID: shikharabhat@gmail.com
Date created: 2021-12-19 15:35:06
Date last modified: 2022-03-15 13:48:40
Purpose: This script defines the main Model class. the Model class is
a simulation of an 'arena' where males and females according to specified
behavioral rules. This code contains bushes (and thus spatial structure),
and, as such, is an improvement over the null model that was the uniform
2D distribution case.
'''

from class_male_and_female import Signaller, Receiver
import random as rd
import matplotlib.pyplot as plt
from scipy.stats import kurtosis, skew
from static_params import *

'''This class is an instance of a 'night'. It contains males and females distributed on a landscape
according to specified parameter values, and then runs an 'experiment' and records the mating success
of various strategies.'''

class Model:
    
    def __init__(self,N_sig,N_rec,landscape,mating_dist=mating_dist,threshold_SPL=threshold_SPL):

        '''
        N_sig is number of signallers
        N_rec is number of receivers
        landscape is the object (of class Landscape) where the simulation will take place
        threshold_SPL is the sensitivity of the receiver in dB
        mating_dist is the maximum distance between a male and a female which can be considered as a mating
        '''
        self.N_sig = int(N_sig)
        self.N_rec = int(N_rec)
        self.callerlist = []
        self.receiverlist = []
        self.threshold_SPL = threshold_SPL
        self.mating_dist = mating_dist
        self.night_dur = night_dur
        self.landscape = landscape

        #male velocities are drawn from a lognormal distribution
        male_vel = np.random.lognormal(male_vel_mean,male_vel_sd,size=int(N_sig))

        #decompose into orthogonal components
        male_vel /= np.sqrt(2)

        self.male_vel_list = male_vel

        #Make a truncated normal distribution that is within (0,1]
        call_effort = np.zeros((0,)) #empty list to fill below
        while call_effort.shape[0] < N_sig:
            sample = np.random.normal(effort_mean,effort_sd,size=(int(N_sig),))

            #only accept those samples which are in (0,1]
            accepted = sample[(sample>0)&(sample<=1)]
            call_effort = np.concatenate((call_effort,accepted),axis=0)
        call_effort = call_effort[:int(N_sig)] #discard extra values

        self.call_effort = list((call_effort).flatten())
    
    #Make the signallers (males)
    def gen_callers(self,baffle_prop,SPL,side): 
        
        #baffle_prop is proportion of N_sig that use baffles
        
        callerlist = []
        baffle_num = int(round(baffle_prop*self.N_sig))
                
        #Make bafflers
        for i in range(0,(baffle_num)): #Make as many bafflers as specified by baffle_num
            
            #Make the signaller
            #SPL of the signaller is drawn from a Normal dist with specified mean and sd
            caller = Signaller(0,0,np.random.normal(loc=SPL,scale=SPL_sd),rd.choice(self.call_effort),baffler=True)

            #Assign the caller a location within one of the bushes present in the landscape
            self.landscape.assign_locations(caller)

            #Append to list of all callers
            callerlist.append(caller)
        
        #Make non-bafflers
        #We'll distinguish between callers and silent males later
        for i in range(0,int(self.N_sig)-baffle_num):

            #Make the signaller
            #SPL of the signaller is drawn from a Normal dist with specified mean and sd
            caller = Signaller(0,0,np.random.normal(loc=SPL,scale=SPL_sd),rd.choice(self.call_effort),baffler=False)

            #Assign the caller a location within one of the bushes present in the landscape
            self.landscape.assign_locations(caller)

            #Append to list of all callers
            callerlist.append(caller)
        
        rd.shuffle(callerlist) #shuffle is just to make the order random
        
        self.callerlist = callerlist
        del callerlist #To save memory
    
    #Make the receivers (females)
    def gen_receivers(self,velx,vely,side):
        
        '''
        fem_mov_prop is the average movement propensity of a female
        velx and vely are the x and y components of the velocity of females (array of values)
        these values are from data in the lab
        current values are for across-bush, will be modified to make it within-bush later
        '''
        
        reclist = []    

        for i in range(0,self.N_rec):

            receiver = Receiver(0,0,rd.choice(velx),rd.choice(vely))

            #Assign the receiver a location within one of the bushes present in the landscape
            self.landscape.assign_locations(receiver)

            #Append to list of all recievers
            reclist.append(receiver)
        
        #shuffle is just so that the order is random, to prevent any accidental systemic biases
        rd.shuffle(reclist)
        self.receiverlist = reclist
        del reclist #To save memory
    
    #Simulate phonotaxis
    def phonotaxis(self):

        '''
        this function implements proabilistic phonotaxis according to perceived call amplitude. The 
        phonotaxis function is from Rittik's data. 
        '''  
        

        '''phonotaxis performed by females'''
        for receiver in self.receiverlist:
            
            if receiver.mating: #Individuals can't perform phonotaxis when they're mating
                continue
            
            #Find out which males/bushes are audible to the female and find out their corresponding SPLs
            callers,SPLs,audible_bushes,bush_dists,bush_SPLs = receiver.listen(self.threshold_SPL)
            audible_bushes = np.array(audible_bushes)
            bush_dists = np.array(bush_dists)


            if rd.uniform(0,1) <= fem_mov_prop_within_bush:
                if receiver.mated_count: #If a female has already mated, it doesn't perform phonotaxis and instead moves randomly depending on mated phonotaxis propensity criteria
                    if np.random.uniform(0,1) > mated_phonotaxis_prop:
                        temp_x = receiver.x             #Temporary variable that holds value of x coordinate to calculate distance moved across bush
                        temp_y = receiver.y             #Temporary variable that holds value of x coordinate to calculate distance moved across bush
                        receiver.move(receiver.bush.assign_locations_in_bush())
                        receiver.within_bush_steps +=1          ##Stores total number of across bush steps moved by caller
                        receiver.within_bush_distance += np.sqrt((receiver.x-temp_x)**2 + (receiver.y-temp_y)**2) #Stores total across bush distance moved
                        continue

                if len(callers): #If the female has heard males
                    SPLs = np.array(SPLs,dtype='object')
    
                    #Find the loudest males
                    focal_SPL = max(SPLs)
                    #pick a random male subject to amplitude resolution constraint (enforced by threshold_SPL_diff)
                    loudest_caller = callers[rd.choice(np.where(abs(SPLs - max(SPLs))<threshold_SPL_diff)[0])]
                    
                    if focal_SPL/min_SPL_for_movement >= np.random.uniform(): #Probabilistic phonotaxis, dependent on amplitude
                                            
                        '''gradually move to location according to specified velocity'''
                        temp_x = receiver.x             #Temporary variable that holds value of x coordinate to calculate distance moved across bush
                        temp_y =receiver.y             #Temporary variable that holds value of x coordinate to calculate distance moved across bush
                        receiver.move((loudest_caller.x,loudest_caller.y))
                        receiver.within_bush_phonotaxis_steps +=1          ##Stores total number of across bush steps moved by caller
                        receiver.within_bush_phonotaxis_distance += np.sqrt((receiver.x-temp_x)**2 + (receiver.y-temp_y)**2) #Stores total across bush distance moved
                        
                    del loudest_caller, focal_SPL #to save memory
                    continue
                #If female does not hear males within a bush
                else:
                    temp_x = receiver.x             #Temporary variable that holds value of x coordinate to calculate distance moved across bush
                    temp_y = receiver.y             #Temporary variable that holds value of x coordinate to calculate distance moved across bush
                    receiver.move(receiver.bush.assign_locations_in_bush())
                    receiver.within_bush_steps +=1          ##Stores total number of across bush steps moved by caller
                    receiver.within_bush_distance += np.sqrt((receiver.x-temp_x)**2 + (receiver.y-temp_y)**2)
                    continue
                
                
            #Decide whether to move to a new bush   
            # if rd.uniform(0,1) <= fem_mov_prop_across_bush:
            #     if receiver.mated_count: #If a female has already mated, it doesn't perform phonotaxis and instead moves randomly depending on mated phonotaxis propensity criteria
            #         if np.random.uniform(0,1) > mated_phonotaxis_prop:
            #             #If female is not doing phonotaxis,it moves to a random bush
            #             if len(receiver.bush.adj_bushes):

            #                 #adj_bushes stores values as (bush,distance)
            #                 bush_distr = [var[0] for var in receiver.bush.adj_bushes]
            #                 distance_distr = [var[1] for var in receiver.bush.adj_bushes]

            #                 bush_distr = np.array(bush_distr)
            #                 distance_distr = np.array(distance_distr)

            #                 #Find potential bushes according to specified lognormal distribution
            #                 distance_distr = np.array(distance_distr)
            #                 cut_off_distance = np.random.lognormal(fem_dist_mean,fem_dist_sd,size=1)
            #                 potential_bushes = bush_distr[distance_distr <= cut_off_distance]
                            
            #                 if len(potential_bushes):

            #                 #pick one of the acceptable bushes at random
            #                     new_bush = rd.choice(potential_bushes)
    
            #                     receiver_index = receiver.bush.find_cricket_index(receiver)
            #                     receiver = receiver.bush.receiverlist.pop(receiver_index)
                        
            #                     #Move this female to its new bush
            #                     receiver.bush = new_bush
            #                     new_bush.receiverlist.append(receiver)
            #                     temp_x = receiver.x             #Temporary variable that hold value of x coordinate to calculate distance moved across bush
            #                     temp_y = receiver.y              #Temporary variable that hold value of x coordinate to calculate distance moved across bush
            #                     new_bush.assign_locations_in_bush(receiver)
            #                     receiver.across_bush_steps +=1          #Stores total number of across bush steps moved by caller
            #                     receiver.across_bush_distance += np.sqrt((receiver.x-temp_x)**2 + (receiver.y-temp_y)**2) #Stores total across bush distance moved
    
            #                     #Move on to the next female
            #                     continue
            #     #If female can hear males across bushes and can do phonotaxis,following statements are executed
            #     if len(audible_bushes) and len(receiver.bush.adj_bushes):

            #             bush_SPLs = np.array(bush_SPLs,dtype='object')

            #             #Find the loudest bushes subject to amplitude resolution constraints
            #             bush_indices = np.where(abs(bush_SPLs - max(bush_SPLs))<threshold_SPL_diff)[0]

            #             loud_bushes = audible_bushes[bush_indices]
            #             bush_dists = bush_dists[bush_indices]

            #             #sample according to lognormal dist
            #             potential_bushes = []
            #             while not len(potential_bushes):
            #                 cut_off_distance = np.random.lognormal(fem_dist_mean,fem_dist_sd,size=1)
            #                 potential_bushes = loud_bushes[bush_dists <= cut_off_distance]
                        
            #             #pick one of these bushes at random
            #             loudest_bush = rd.choice(potential_bushes)

            #             #remove the receiver from its original bush
            #             receiver_index = receiver.bush.find_cricket_index(receiver)
            #             receiver = receiver.bush.receiverlist.pop(receiver_index)

            #             #Move this receiver to its new bush
            #             receiver.bush = loudest_bush
            #             loudest_bush.receiverlist.append(receiver)
            #             temp_x = receiver.x             #Temporary variable that hold value of x coordinate to calculate distance moved across bush
            #             temp_y = receiver.y              #Temporary variable that hold value of x coordinate to calculate distance moved across bush
            #             loudest_bush.assign_locations_in_bush(receiver)
            #             receiver.across_bush_phonotaxis_steps +=1          #Stores total number of across bush steps moved by caller
            #             receiver.across_bush_phonotaxis_distance += np.sqrt((receiver.x-temp_x)**2 + (receiver.y-temp_y)**2) #Stores total across bush distance moved
            #             #Move on to the next receiver
            #             continue
                    
            #         #random movement across bushes if the phonotactic female does not hear anything
            #     elif len(receiver.bush.adj_bushes):

            #             #adj_bushes stores values as (bush,distance)
            #             bush_distr = [var[0] for var in receiver.bush.adj_bushes]
            #             distance_distr = [var[1] for var in receiver.bush.adj_bushes]

            #             bush_distr = np.array(bush_distr)
            #             distance_distr = np.array(distance_distr)

            #             #Find potential bushes according to specified lognormal distribution
            #             distance_distr = np.array(distance_distr)
            #             cut_off_distance = np.random.lognormal(fem_dist_mean,fem_dist_sd,size=1)
            #             potential_bushes = bush_distr[distance_distr <= cut_off_distance]
                        
            #             if len(potential_bushes):

            #                 #pick one of the acceptable bushes at random
            #                 new_bush = rd.choice(potential_bushes)
    
            #                 receiver_index = receiver.bush.find_cricket_index(receiver)
            #                 receiver = receiver.bush.receiverlist.pop(receiver_index)
                    
            #                 #Move this female to its new bush
            #                 receiver.bush = new_bush
            #                 new_bush.receiverlist.append(receiver)
                            
            #                 temp_x = receiver.x             #Temporary variable that hold value of x coordinate to calculate distance moved across bush
            #                 temp_y = receiver.y             #Temporary variable that hold value of x coordinate to calculate distance moved across bush
            #                 new_bush.assign_locations_in_bush(receiver)
            #                 receiver.across_bush_steps +=1          #Stores total number of across bush steps moved by caller
            #                 receiver.across_bush_distance += np.sqrt((receiver.x-temp_x)**2 + (receiver.y-temp_y)**2) #Stores total across bush distance moved
    
            #                 #Move on to the next female
            #                 continue

        
        '''movement performed by males'''
        for caller in self.callerlist:

            
            if caller.mating or caller.baffler: #males can't move while mating or baffling
                continue
            #Males do not perform phonotaxis, they simply move around randomly
            #Decide whether or not to move within the same bush based on your movement propensity
            if rd.uniform(0,1) <= male_mov_prop_within_bush:

                temp_x = caller.x             #Temporary variable that holds value of x coordinate to calculate distance moved across bush
                temp_y = caller.y             #Temporary variable that holds value of x coordinate to calculate distance moved across bush
                caller.move(caller.bush.assign_locations_in_bush())
                caller.within_bush_steps +=1          ##Stores total number of across bush steps moved by caller
                caller.within_bush_distance += np.sqrt((caller.x-temp_x)**2 + (caller.y-temp_y)**2) #Stores total across bush distance moved
                continue
            #Decide whether or not to move wacross bushes based on your movement propensity
            # if rd.uniform (0,1) <=male_mov_prop_across_bush and len(caller.bush.adj_bushes):

            #     bush_distr = [var[0] for var in caller.bush.adj_bushes]
            #     distance_distr = [var[1] for var in caller.bush.adj_bushes]
            #     bush_distr = np.array(bush_distr)
            #     distance_distr = np.array(distance_distr)

            #     #Find potential bushes according to specified lognormal distribution
            #     cut_off_distance = np.random.lognormal(male_dist_mean,male_dist_sd,size=1)
            #     potential_bushes = bush_distr[distance_distr <= cut_off_distance]

            #     if len(potential_bushes)>0:
            #         new_bush = rd.choice(potential_bushes)  #pick one of the acceptable bushes at random
            #         caller_index = caller.bush.find_cricket_index(caller)
            #         caller = caller.bush.callerlist.pop(caller_index)
                    
            #         #Move this caller to its new bush
            #         caller.bush = new_bush
            #         new_bush.callerlist.append(caller)
            #         temp_x = caller.x             #Temporary variable that hold value of x coordinate to calculate distance moved across bush
            #         temp_y = caller.y              #Temporary variable that hold value of x coordinate to calculate distance moved across bush
            #         new_bush.assign_locations_in_bush(caller)
            #         caller.across_bush_steps +=1          #Stores total number of across bush steps moved by caller
            #         caller.across_bush_distance += np.sqrt((caller.x-temp_x)**2 + (caller.y-temp_y)**2) #Stores total across bush distance moved
            #         continue
                

            
            
        
    def mate(self,time):

        '''
        this function implements mating.
        A male and a female mate if they are less than a specified distance apart
        Once they begin mating, they are mating for some period and have a refractory period during
        which they cannot mate again.
        '''
        
        for receiver in self.receiverlist:
                
                if receiver.mating: #If reciever is already mating, skip it
                    continue
                
                #Find out which males are close to the focal female on the same bush
                close_callers = []
                for caller in self.callerlist:
                    if caller.dist(receiver) < self.mating_dist and not caller.mating:
                        close_callers.append(caller)
                        
                if len(close_callers):
                    
                    lucky_caller = rd.choice(close_callers) #Choose one of the males within threshold distance
                    lucky_caller.mating = True
                    receiver.mating = True

                    #keep track of which strategies the focal female is mating with
                    receiver.mated_male_type.extend((lucky_caller.baffler,time))

                    #add to total mate counts of each individual
                    lucky_caller.mated_count += 1
                    receiver.mated_count += 1
                    
                    #del lucky_caller #to save memory

        for caller in self.callerlist:
            if caller.mating:
                caller.mating_timer += 1 #keep track of how long each individual has been mating for
            if caller.mating_timer % mating_duration == 0: #if it is done mating, reset the timer
                caller.mating = False
                caller.mating_timer = 0
        
        for receiver in self.receiverlist:
            if receiver.mating:
                receiver.mating_timer += 1
                if receiver.mating_timer % mating_duration == 0:

                    receiver.mating = False
                    receiver.mating_timer = 0

                
                    #Move the receiver to a random bush once it mates

                    #remove the receiver from the bush
                    receiver_index = receiver.bush.find_cricket_index(receiver)
                    receiver = receiver.bush.receiverlist.pop(receiver_index)

                    #add it to a new bush in the landscape
                    self.landscape.assign_locations(receiver)                                  

    def decide_to_call(self):

        '''
        this function lets each caller decide the times during which it will call in a given night
        the difference between callers and silent males is implemented here
        '''

        #seperate the bafflers from the non-bafflers
        #this is necessary because baffling trait frequency is a parameter of the model
        non_bafflers = []
        bafflers = []
        for caller in self.callerlist:
            if caller.baffler:
                bafflers.append(caller)
            else:
                non_bafflers.append(caller)

        #Decide how many males (among the non-bafflers) are going to be callers
        #male_call_prop is from data
        num_callers = int(round(len(non_bafflers)*male_call_prop))    
        callers = np.random.choice(non_bafflers,num_callers,replace=False)
        
        #Assign calling times to the bafflers
        for caller in bafflers:
            effort = int(round(caller.call_effort*decision_dur))
            caller.call_times = np.random.randint(0,decision_dur,effort)

        #Assign calling times and velocities to the non-baffling callers 
        for caller in callers:
            effort = int(round(caller.call_effort*decision_dur))
            caller.call_times = np.random.randint(0,decision_dur,effort)
                 
            caller.velx = rd.choice(self.male_vel_list)
            caller.vely = rd.choice(self.male_vel_list)
        
        #Remaining males are silent males and do not call at all
        for caller in self.callerlist:
            
            #If a male wasn't selected in the previous two loops,
            #its call times would be an empty list
            if not len(caller.call_times): 
                caller.velx = rd.choice(self.male_vel_list)
                caller.vely = rd.choice(self.male_vel_list)

        del callers, bafflers, non_bafflers #to save memory

    def call(self,time):

        '''
        this function implements actual calling based on the call times
        determined in the previous function
        '''
        
        for caller in self.callerlist:
            if len(caller.call_times) and not caller.mating: #If the male actually intends to call
                for call_time in caller.call_times:
                    if time % decision_dur == call_time: #If the time is right
                        caller.calling = True #Start calling
                        caller.call_instances +=1
                        break
                    else:
                        caller.calling = False #Don't call
                              #keeps track of number of sessions a caller calls
            else:
                caller.calling = False

    def run(self, timesteps,side,store_images=False,directory=''):

        '''
        implement all the functions defined above to actually run a simulation
        for a given length of time (specified by timesteps)
        '''

        time = 0
        while time < timesteps:

            #shuffle is to randomize the order of individuals each time
            rd.shuffle(self.callerlist)
            rd.shuffle(self.receiverlist)

            #not relevant if we only run for a single night
            if time%decision_dur == 0:
                self.decide_to_call()
            
            self.call(time) #calling
            self.phonotaxis() #movement + phonotaxis
            self.mate(time) #mating
            
            #reset mating status each night
            if time % night_dur == 0:
                for receiver in self.receiverlist:
                    receiver.mated_count = 0 #Reset mate counts of receivers each night
            
            #for visualization purposes
            if store_images:
                filename = directory+str(time)+'.png'
                self.visualize(time,True,filename)
            
            #progress to next timestep
            time += 1
            
    def get_mate_counts(self,baffle_prop):

        '''
        get the average mating success per individual for each of the three strategies
        this will be the 'output' of our model, and we will use mating success as a 
        proxy for fitness.
        '''

        #initialize empty lists
        baffle_matings = []
        baffle_call_effort = []
        baffle_within_bush_steps = []
        baffle_within_bush_distance = []
        baffle_across_bush_steps = []
        baffle_across_bush_distance = []
        baffle_total_steps = []
        baffle_total_distance = []
        
        caller_matings = []
        caller_call_effort = []
        caller_within_bush_steps = []
        caller_within_bush_distance = []
        caller_across_bush_steps = []
        caller_across_bush_distance = []
        caller_total_steps = []
        caller_total_distance = []
        
        silent_matings = []
        silent_call_effort = []
        silent_within_bush_steps = []
        silent_within_bush_distance = []
        silent_across_bush_steps = []
        silent_across_bush_distance = []
        silent_total_steps = []
        silent_total_distance = []
        
        
        rec_matings = []
        rec_within_bush_steps = []
        rec_within_bush_distance = []
        rec_across_bush_steps = []
        rec_across_bush_distance = []
        rec_within_bush_phonotaxis_steps = []
        rec_within_bush_phonotaxis_distance = []
        rec_across_bush_phonotaxis_steps = []
        rec_across_bush_phonotaxis_distance = []
        rec_within_bush_total_steps = []
        rec_within_bush_total_distance = []
        rec_across_bush_total_steps = []
        rec_across_bush_total_distance = []
        rec_total_steps = []
        rec_total_distance = []
        
        
        mated_maletypes =[]

        #count number of mates obtained by each strategy
        for caller in self.callerlist:
            if caller.baffler:
                baffle_matings.append(caller.mated_count)
                baffle_call_effort.append(caller.call_instances)
                baffle_within_bush_steps.append(caller.within_bush_steps)
                baffle_within_bush_distance.append(caller.within_bush_distance)
                baffle_across_bush_steps.append(caller.across_bush_steps)
                baffle_across_bush_distance.append(caller.across_bush_distance)
                baffle_total_steps.append(caller.within_bush_steps + caller.across_bush_steps)
                baffle_total_distance.append(caller.within_bush_distance + caller.across_bush_distance)
                
            else:
                if len(caller.call_times) != 0:
                    caller_matings.append(caller.mated_count)
                    caller_call_effort.append(caller.call_instances)
                    caller_within_bush_steps.append(caller.within_bush_steps)
                    caller_within_bush_distance.append(caller.within_bush_distance)
                    caller_across_bush_steps.append(caller.across_bush_steps)
                    caller_across_bush_distance.append(caller.across_bush_distance)
                    caller_total_steps.append(caller.within_bush_steps + caller.across_bush_steps)
                    caller_total_distance.append(caller.within_bush_distance + caller.across_bush_distance)
                else:
                    silent_matings.append(caller.mated_count)
                    silent_call_effort.append(caller.call_instances)
                    silent_within_bush_steps.append(caller.within_bush_steps)
                    silent_within_bush_distance.append(caller.within_bush_distance)
                    silent_across_bush_steps.append(caller.across_bush_steps)
                    silent_across_bush_distance.append(caller.across_bush_distance)
                    silent_total_steps.append(caller.within_bush_steps + caller.across_bush_steps)
                    silent_total_distance.append(caller.within_bush_distance + caller.across_bush_distance)
           

        #track how many times each female mated and which strategies each female mated with
        for receiver in self.receiverlist:
            rec_matings.append(receiver.mated_count)
            rec_within_bush_steps.append(receiver.within_bush_steps)
            rec_within_bush_distance.append(receiver.within_bush_distance)
            rec_within_bush_phonotaxis_steps.append(receiver.within_bush_phonotaxis_steps)
            rec_within_bush_phonotaxis_distance.append(receiver.within_bush_phonotaxis_distance)
            rec_within_bush_total_steps.append(receiver.within_bush_steps + receiver.within_bush_phonotaxis_steps)
            rec_within_bush_total_distance.append(receiver.within_bush_distance + receiver.within_bush_phonotaxis_distance)
            rec_across_bush_steps.append(receiver.across_bush_steps)
            rec_across_bush_distance.append(receiver.across_bush_distance)
            rec_across_bush_phonotaxis_steps.append(receiver.across_bush_phonotaxis_steps)
            rec_across_bush_phonotaxis_distance.append(receiver.across_bush_phonotaxis_distance)
            rec_across_bush_total_steps.append(receiver.across_bush_steps + receiver.across_bush_phonotaxis_steps)
            rec_across_bush_total_distance.append(receiver.across_bush_distance + receiver.across_bush_phonotaxis_distance)
            rec_total_steps.append(receiver.within_bush_steps + receiver.within_bush_phonotaxis_steps + receiver.across_bush_steps + receiver.across_bush_phonotaxis_steps)
            rec_total_distance.append(receiver.within_bush_distance + receiver.within_bush_phonotaxis_distance + receiver.across_bush_distance + receiver.across_bush_phonotaxis_distance)
            
            
            if len(receiver.mated_male_type)>0:
                mated_maletypes.append(receiver.mated_male_type)
        
        #convert lists to arrays
        total_male_matings = np.array(baffle_matings+caller_matings+silent_matings) #adding lists concatenates them
        
        baffle_matings = np.array(baffle_matings)
        baffle_call_effort = np.array(baffle_call_effort)
        baffle_within_bush_steps = np.array(baffle_within_bush_steps)
        baffle_within_bush_distance = np.array(baffle_within_bush_distance)
        baffle_across_bush_steps = np.array(baffle_across_bush_steps)
        baffle_across_bush_distance = np.array(baffle_across_bush_distance)
        baffle_total_steps = np.array(baffle_total_steps)
        baffle_total_distance = np.array(baffle_total_distance)
        
        caller_matings = np.array(caller_matings)
        caller_call_effort = np.array(caller_call_effort)
        caller_within_bush_steps = np.array(caller_within_bush_steps)
        caller_within_bush_distance = np.array(caller_within_bush_distance)
        caller_across_bush_steps = np.array(caller_across_bush_steps)
        caller_across_bush_distance = np.array(caller_across_bush_distance)
        caller_total_steps = np.array(caller_total_steps)
        caller_total_distance = np.array(caller_total_distance)
        
        silent_matings = np.array(silent_matings)
        silent_call_effort = np.array(silent_call_effort)
        silent_within_bush_steps = np.array(silent_within_bush_steps)
        silent_within_bush_distance = np.array(silent_within_bush_distance)
        silent_across_bush_steps = np.array(silent_across_bush_steps)
        silent_across_bush_distance = np.array(silent_across_bush_distance)
        silent_total_steps = np.array(silent_total_steps)
        silent_total_distance = np.array(silent_total_distance)
        
        
        rec_matings = np.array(rec_matings)
        rec_within_bush_steps = np.array(rec_within_bush_steps)
        rec_within_bush_distance = np.array(rec_within_bush_distance)
        rec_across_bush_steps = np.array(rec_across_bush_steps)
        rec_across_bush_distance = np.array(rec_across_bush_distance)
        rec_within_bush_phonotaxis_steps = np.array(rec_within_bush_phonotaxis_steps)
        rec_within_bush_phonotaxis_distance = np.array(rec_within_bush_phonotaxis_distance)
        rec_across_bush_phonotaxis_steps = np.array(rec_across_bush_phonotaxis_steps)
        rec_across_bush_phonotaxis_distance = np.array(rec_across_bush_phonotaxis_distance)
        rec_within_bush_total_steps = np.array(rec_within_bush_total_steps)
        rec_within_bush_total_distance = np.array(rec_within_bush_total_distance)
        rec_across_bush_total_steps = np.array(rec_across_bush_total_steps)
        rec_across_bush_total_distance = np.array(rec_across_bush_total_distance)
        rec_total_steps = np.array(rec_total_steps)
        rec_total_distance = np.array(rec_total_distance)
        
        

        #mean mating success
        mean_list = [np.mean(baffle_matings),np.mean(caller_matings),np.mean(silent_matings),
                             np.mean(total_male_matings),np.mean(rec_matings),
                             
                             np.mean(baffle_call_effort),np.mean(baffle_within_bush_steps),
                             np.mean(baffle_within_bush_distance),np.mean(baffle_across_bush_steps),np.mean(baffle_across_bush_distance),
                             np.mean(baffle_total_steps),np.mean(baffle_total_distance),
                             
                             np.mean(caller_call_effort),np.mean(caller_within_bush_steps),
                             np.mean(caller_within_bush_distance),np.mean(caller_across_bush_steps),np.mean(caller_across_bush_distance),
                             np.mean(caller_total_steps),np.mean(caller_total_distance),
                             
                             np.mean(silent_call_effort),np.mean(silent_within_bush_steps),
                             np.mean(silent_within_bush_distance),np.mean(silent_across_bush_steps),np.mean(silent_across_bush_distance),
                             np.mean(silent_total_steps),np.mean(silent_total_distance),
                             
                             np.mean(rec_within_bush_steps),np.mean(rec_within_bush_distance),np.mean(rec_across_bush_steps),np.mean(rec_across_bush_distance),
                             np.mean(rec_within_bush_phonotaxis_steps),np.mean(rec_within_bush_phonotaxis_distance),np.mean(rec_across_bush_phonotaxis_steps),
                             np.mean(rec_across_bush_phonotaxis_distance),np.mean(rec_within_bush_total_steps),np.mean(rec_within_bush_total_distance),
                             np.mean(rec_across_bush_total_steps),np.mean(rec_across_bush_total_distance),
                             np.mean(rec_total_steps),np.mean(rec_total_distance)]

        #sd mating success
        sd_list = [np.std(baffle_matings),np.std(caller_matings),np.std(silent_matings),
                             np.std(total_male_matings),np.std(rec_matings),
                             
                             np.std(baffle_call_effort),np.std(baffle_within_bush_steps),
                             np.std(baffle_within_bush_distance),np.std(baffle_across_bush_steps),np.std(baffle_across_bush_distance),
                             np.std(baffle_total_steps),np.std(baffle_total_distance),
                             
                             np.std(caller_call_effort),np.std(caller_within_bush_steps),
                             np.std(caller_within_bush_distance),np.std(caller_across_bush_steps),np.std(caller_across_bush_distance),
                             np.std(caller_total_steps),np.std(caller_total_distance),
                             
                             np.std(silent_call_effort),np.std(silent_within_bush_steps),
                             np.std(silent_within_bush_distance),np.std(silent_across_bush_steps),np.std(silent_across_bush_distance),
                             np.std(silent_total_steps),np.std(silent_total_distance),
                             
                             np.std(rec_within_bush_steps),np.std(rec_within_bush_distance),np.std(rec_across_bush_steps),np.std(rec_across_bush_distance),
                             np.std(rec_within_bush_phonotaxis_steps),np.std(rec_within_bush_phonotaxis_distance),np.std(rec_across_bush_phonotaxis_steps),
                             np.std(rec_across_bush_phonotaxis_distance),np.std(rec_within_bush_total_steps),np.std(rec_within_bush_total_distance),
                             np.std(rec_across_bush_total_steps),np.std(rec_across_bush_total_distance),
                             np.std(rec_total_steps),np.std(rec_total_distance)]

        #kurtosis of mating success
        kurt_list = [kurtosis(baffle_matings),kurtosis(caller_matings),kurtosis(silent_matings),
                    kurtosis(total_male_matings), kurtosis(rec_matings),
                    
                    kurtosis(baffle_call_effort),kurtosis(baffle_within_bush_steps),
                    kurtosis(baffle_within_bush_distance),kurtosis(baffle_across_bush_steps),kurtosis(baffle_across_bush_distance),
                    kurtosis(baffle_total_steps),kurtosis(baffle_total_distance),
                    
                    kurtosis(caller_call_effort),kurtosis(caller_within_bush_steps),
                    kurtosis(caller_within_bush_distance),kurtosis(caller_across_bush_steps),kurtosis(caller_across_bush_distance),
                    kurtosis(caller_total_steps),kurtosis(caller_total_distance),
                    
                    kurtosis(silent_call_effort),kurtosis(silent_within_bush_steps),
                    kurtosis(silent_within_bush_distance),kurtosis(silent_across_bush_steps),kurtosis(silent_across_bush_distance),
                    kurtosis(silent_total_steps),kurtosis(silent_total_distance),
                    
                    kurtosis(rec_within_bush_steps),kurtosis(rec_within_bush_distance),kurtosis(rec_across_bush_steps),kurtosis(rec_across_bush_distance),
                    kurtosis(rec_within_bush_phonotaxis_steps),kurtosis(rec_within_bush_phonotaxis_distance),kurtosis(rec_across_bush_phonotaxis_steps),
                    kurtosis(rec_across_bush_phonotaxis_distance),kurtosis(rec_within_bush_total_steps),kurtosis(rec_within_bush_total_distance),
                    kurtosis(rec_across_bush_total_steps),kurtosis(rec_across_bush_total_distance),
                    kurtosis(rec_total_steps),kurtosis(rec_total_distance)]
        #skew of mating success
        skew_list = [skew(baffle_matings),skew(caller_matings),skew(silent_matings),
                     skew(total_male_matings), skew(rec_matings),
                     
                     skew(baffle_call_effort),skew(baffle_within_bush_steps),
                     skew(baffle_within_bush_distance),skew(baffle_across_bush_steps),skew(baffle_across_bush_distance),
                     skew(baffle_total_steps),skew(baffle_total_distance),
                     
                     skew(caller_call_effort),skew(caller_within_bush_steps),
                     skew(caller_within_bush_distance),skew(caller_across_bush_steps),skew(caller_across_bush_distance),
                     skew(caller_total_steps),skew(caller_total_distance),
                     
                     skew(silent_call_effort),skew(silent_within_bush_steps),
                     skew(silent_within_bush_distance),skew(silent_across_bush_steps),skew(silent_across_bush_distance),
                     skew(silent_total_steps),skew(silent_total_distance),
                     
                     skew(rec_within_bush_steps),skew(rec_within_bush_distance),skew(rec_across_bush_steps),skew(rec_across_bush_distance),
                     skew(rec_within_bush_phonotaxis_steps),skew(rec_within_bush_phonotaxis_distance),skew(rec_across_bush_phonotaxis_steps),
                     skew(rec_across_bush_phonotaxis_distance),skew(rec_within_bush_total_steps),skew(rec_within_bush_total_distance),
                     skew(rec_across_bush_total_steps),skew(rec_across_bush_total_distance),
                     skew(rec_total_steps),skew(rec_total_distance)]

        #min
        min_list = [np.min(baffle_matings),np.min(caller_matings),np.min(silent_matings),
                   np.min(total_male_matings), np.min(rec_matings),
                   
                   np.min(baffle_call_effort),np.min(baffle_within_bush_steps),
                   np.min(baffle_within_bush_distance),np.min(baffle_across_bush_steps),np.min(baffle_across_bush_distance),
                   np.min(baffle_total_steps),np.min(baffle_total_distance),
                   
                   np.min(caller_call_effort),np.min(caller_within_bush_steps),
                   np.min(caller_within_bush_distance),np.min(caller_across_bush_steps),np.min(caller_across_bush_distance),
                   np.min(caller_total_steps),np.min(caller_total_distance),
                   
                   np.min(silent_call_effort),np.min(silent_within_bush_steps),
                   np.min(silent_within_bush_distance),np.min(silent_across_bush_steps),np.min(silent_across_bush_distance),
                   np.min(silent_total_steps),np.min(silent_total_distance),
                   
                   np.min(rec_within_bush_steps),np.min(rec_within_bush_distance),np.min(rec_across_bush_steps),np.min(rec_across_bush_distance),
                   np.min(rec_within_bush_phonotaxis_steps),np.min(rec_within_bush_phonotaxis_distance),np.min(rec_across_bush_phonotaxis_steps),
                   np.min(rec_across_bush_phonotaxis_distance),np.min(rec_within_bush_total_steps),np.min(rec_within_bush_total_distance),
                   np.min(rec_across_bush_total_steps),np.min(rec_across_bush_total_distance),
                   np.min(rec_total_steps),np.min(rec_total_distance)]

        #max
        max_list = [np.max(baffle_matings),np.max(caller_matings),np.max(silent_matings),
                   np.max(total_male_matings), np.max(rec_matings),
                   
                   np.max(baffle_call_effort),np.max(baffle_within_bush_steps),
                   np.max(baffle_within_bush_distance),np.max(baffle_across_bush_steps),np.max(baffle_across_bush_distance),
                   np.max(baffle_total_steps),np.max(baffle_total_distance),
                   
                   np.max(caller_call_effort),np.max(caller_within_bush_steps),
                   np.max(caller_within_bush_distance),np.max(caller_across_bush_steps),np.max(caller_across_bush_distance),
                   np.max(caller_total_steps),np.max(caller_total_distance),
                   
                   np.max(silent_call_effort),np.max(silent_within_bush_steps),
                   np.max(silent_within_bush_distance),np.max(silent_across_bush_steps),np.max(silent_across_bush_distance),
                   np.max(silent_total_steps),np.max(silent_total_distance),
                   
                   np.max(rec_within_bush_steps),np.max(rec_within_bush_distance),np.max(rec_across_bush_steps),np.max(rec_across_bush_distance),
                   np.max(rec_within_bush_phonotaxis_steps),np.max(rec_within_bush_phonotaxis_distance),np.max(rec_across_bush_phonotaxis_steps),
                   np.max(rec_across_bush_phonotaxis_distance),np.max(rec_within_bush_total_steps),np.max(rec_within_bush_total_distance),
                   np.max(rec_across_bush_total_steps),np.max(rec_across_bush_total_distance),
                   np.max(rec_total_steps),np.max(rec_total_distance)]

        #median
        median_list = [np.median(baffle_matings),np.median(caller_matings),np.median(silent_matings),
                   np.median(total_male_matings), np.median(rec_matings),
                   
                   np.median(baffle_call_effort),np.median(baffle_within_bush_steps),
                   np.median(baffle_within_bush_distance),np.median(baffle_across_bush_steps),np.median(baffle_across_bush_distance),
                   np.median(baffle_total_steps),np.median(baffle_total_distance),
                   
                   np.median(caller_call_effort),np.median(caller_within_bush_steps),
                   np.median(caller_within_bush_distance),np.median(caller_across_bush_steps),np.median(caller_across_bush_distance),
                   np.median(caller_total_steps),np.median(caller_total_distance),
                   
                   np.median(silent_call_effort),np.median(silent_within_bush_steps),
                   np.median(silent_within_bush_distance),np.median(silent_across_bush_steps),np.median(silent_across_bush_distance),
                   np.median(silent_total_steps),np.median(silent_total_distance),
                   
                   np.median(rec_within_bush_steps),np.median(rec_within_bush_distance),np.median(rec_across_bush_steps),np.median(rec_across_bush_distance),
                   np.median(rec_within_bush_phonotaxis_steps),np.median(rec_within_bush_phonotaxis_distance),np.median(rec_across_bush_phonotaxis_steps),
                   np.median(rec_across_bush_phonotaxis_distance),np.median(rec_within_bush_total_steps),np.median(rec_within_bush_total_distance),
                   np.median(rec_across_bush_total_steps),np.median(rec_across_bush_total_distance),
                   np.median(rec_total_steps),np.median(rec_total_distance)]
                   
         #proportion of inds who obtained mates
        mated_prop_list = [len(baffle_matings[baffle_matings>0])/len(baffle_matings),len(caller_matings[caller_matings>0])/len(caller_matings),
        len(silent_matings[silent_matings>0])/len(silent_matings),len(total_male_matings[total_male_matings>0])/len(total_male_matings),len(rec_matings[rec_matings>0])/len(rec_matings)]          
        

        #return a named dict of values
        #NOTE: mated_maletypes is not being returned here
        return {'mean':mean_list,'sd':sd_list,'kurt':kurt_list,'skew':skew_list,'min':min_list,'max':max_list,'median':median_list,'proportion_mated':mated_prop_list}
    
    
    def visualize(self,time,save=False,filename='plot.png'):

        '''
        This is a function that helps visualize what each individual is doing during a run
        NOT necessary for actually running simulations
        '''

        #Adjust plt parameters for prettier plotting
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.rcParams["axes.titleweight"] = "bold"
        plt.rcParams.update({'font.size': 22})

        #these lists will contain the coordinates of individuals for plotting
        normal_cal_x = []
        normal_cal_y = []
        baffle_cal_x = []
        baffle_cal_y = []
        sat_cal_x = []
        sat_cal_y = []
        rec_x = []
        rec_y = []

        #these lists will contain plt.Circle objects which are circles depiciting the
        #active space of calling individuals. I don't really need two seperate lists,
        #I have them now only in case they prove useful later
        caller_circles = []
        baffler_circles = []

        if len(self.callerlist) == 0:
            print ("No signallers in your model")
        for i in range(0,self.N_sig):
            ind = self.callerlist[i]
            if ind.baffler:
                print(ind.x)
                baffle_cal_x.append(ind.x)
                baffle_cal_y.append(ind.y)

                #Add circles which depict the active space of each individual
                if ind.calling:
                    baffler_circles.append(plt.Circle((ind.x,ind.y),ind.find_active_space(),fill=None))
                else:
                    baffler_circles.append(plt.Circle((ind.x,ind.y),0,fill=None))
            else:
                if len(ind.call_times):
                    normal_cal_x.append(ind.x)
                    normal_cal_y.append(ind.y)

                    #Add circles for active space if the individual is calling
                    if ind.calling:
                        caller_circles.append(plt.Circle((ind.x,ind.y),ind.find_active_space(),fill=None))
                    else:
                        caller_circles.append(plt.Circle((ind.x,ind.y),0,fill=None))

                else:
                    sat_cal_x.append(ind.x)
                    sat_cal_y.append(ind.y)

        for i in range(self.N_rec):
            rec_x.append(self.receiverlist[i].x)
            rec_y.append(self.receiverlist[i].y)


        #plot the bushes
        bush_rects = []#This list will contain the plt.Rectangle objects used to show bushes
        for bush in self.landscape.bushlist:

            #create a plt.Rectangle object
            rect = plt.Rectangle((bush.cent_x-bush.bush_size/2,bush.cent_y-bush.bush_size/2),bush.bush_size,bush.bush_size,fc='grey',ec='black',alpha=0.3)
            bush_rects.append(rect)


        #Plot
        fig, ax = plt.subplots(figsize=(8,8))

        #Plot the individuals
        ax.plot(baffle_cal_x,baffle_cal_y,'o',color='red',markersize=3,label='Bafflers')
        ax.plot(normal_cal_x,normal_cal_y,'o',color='blue',markersize=3,label='Callers')
        ax.plot(sat_cal_x,sat_cal_y,'o',color='orange',markersize=3,label='Silent Males')
        ax.plot(rec_x,rec_y,'D',color='green',markersize=3,label='Females')

        #Plot the active spaces
        for circle in baffler_circles:
            ax.add_patch(circle)

        for circle in caller_circles:
            ax.add_patch(circle)

        #plot the bushes
        #for rect in bush_rects:
        #    ax.add_patch(rect)


        #Uncomment below lines if you want a regular grid to be part of the visualization
        #ax.hlines(y=self.landscape.yvals,xmin=0,xmax=self.landscape.xdims[1],color='black',linewidth=1)
        #ax.vlines(x=self.landscape.xvals,ymin=0,ymax=self.landscape.ydims[1],color='black',linewidth=1)


        #Add axes labels and title
        ax.set_xlabel("X position (in cm)")
        ax.set_ylabel("Y position (in cm)")
        ax.set_xlim(self.landscape.xvals[0],self.landscape.xvals[-1])
        ax.set_ylim(self.landscape.yvals[0],self.landscape.yvals[-1])
        ax.set_title("Visualization of simulation",fontsize=22)
        ax.set_xticklabels

        #Add a time counter for how many timesteps have passed
        plt.text(1.2, 0.05, 't = ' + str(time) , fontsize=18, transform=plt.gca().transAxes)
        plt.text(1.2, 0, 'one night = ' + str(night_dur) , fontsize=18, transform=plt.gca().transAxes)

        #Add a legend
        legend = ax.legend(bbox_to_anchor=(1.7,1))

        if save:
            #save to file
            plt.savefig(filename,dpi=200,bbox_extra_artists=(legend,), bbox_inches='tight')
            plt.close()
        else:
            plt.show() 
