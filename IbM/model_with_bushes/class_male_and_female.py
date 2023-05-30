#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Shikhara Bhat
Email ID: shikharabhat@gmail.com
Date created: 2021-10-18 10:25:27
Date last modified: 2022-03-15 13:48:40
Purpose: This script defines the Signaller and Receiver classes. Signallers
will represent the males and receivers will reprsent the females. Both classes
can move in space. Signallers emit signals which propagate through space, and
receivers perceive these signals.
'''

import numpy as np
from static_params import baffle_advantage_mean,baffle_advantage_SD, threshold_SPL

class Signaller: #Traditionally the male, this class represents the individuals which signal for mates
    
    def __init__(self,x,y,SPL,call_effort,baffler):
        
        '''
        x and y describe the position of the signaller in 2D space
        SPL represents the base sound intensity of the signaller in dB SPL (at the source)
        call_effort represents the call effort of the signaller, defined as proportion of
        the night during which the signaller will be calling.
        baffler is a boolean describing whether the signaller is currently using a baffle
        '''
        
        #Position variables (in cm)
        self.x = x
        self.y = y
        self.bush = None #Which bush the individual is located in

        #Velocity variables (in cm/timestep)
        self.velx = 0
        self.vely = 0

        #Call variables
        self.calling = False #Boolean describing whether the signaller is currently calling
        self.baffler = bool(baffler) #Boolean describing whether the signaller is a baffler
        self.call_times = [] #call_times is a list describing the times at which a male will call
        self.call_effort = call_effort
        self.mating = False #To keep track of whether the male is currently mating
        self.mating_timer = 0 #To keep track of mating duration
        
        #If the individual is a baffler, it receives a boost to its SPL
        if self.baffler:
            self.SPL = SPL + np.random.normal(baffle_advantage_mean,baffle_advantage_SD)
        else:
            self.SPL = SPL
        
        #Fitness variables
        self.mated_count = 0 #When initialized, all individuals are unmated
        
        #Movement variables
        self.within_bush_steps = 0
        self.within_bush_distance = 0
        self.across_bush_steps = 0
        self.across_bush_distance = 0
        self.total_steps = 0
        self.total_distance = 0
        
        #Call variables
        self.call_instances = 0        
        

    def __key(self):

        '''
        give each instance a key for unique identification
        Here, the key is based on location, SPL, and whether the male is a baffler
        '''

        return (self.x,self.y,self.SPL,self.baffler)
    
    def __eq__(self, other): 

        '''
        Define a way to compare two Signallers using their attributes
        (to find where an individual is in a set of individuals)
        '''

        if not isinstance(other, Signaller):

            # don't attempt to compare against unrelated classes
            return NotImplemented

        #compare them
        return  self.__key() == other.__key() 
     
    
    def dist(self,caller):
        '''
        this function returns the Euclidean distance from the focal caller to any other caller
        this is currently useless, but could be useful later.

        '''
        xdist = self.x - caller.x
        ydist = self.y - caller.y
        
        return np.sqrt(xdist**2 + ydist**2) #Euclidean distance
    
    def decay(self,dist): 
        
        '''
        Function describing how the call decays with distance. Can be modified as required.
        We currently assume spherical spreading for simplicity.
        '''
            
        if not self.calling:
            return 0
        else:
            if dist > 0:
            
                TL = 20*np.log10(dist/20) #I'm assuming source SPL was measured at a distance of 20cm from the cricket (standard distance for these kind of measurements)
                return self.SPL - TL
        
            else:
                return self.SPL
    
    def move(self,location): #location is a 2-tuple (loc_x,loc_y) that is within the bush

        '''
        this function implements actual movement towards a location based on 
        the velocity of the organism.
        '''
        
        #Find out where to go
        dist = np.sqrt((self.x - location[0])**2+(self.y - location[1])**2)
        
        if dist > 0:
            x,y = (location[0] - self.x)/dist , (location[1]-self.y)/dist #(x,y) is the unit vector pointing from self to location
        else:
            x,y = 0,0
            
        #Move according to your velocity
        
        if dist > np.sqrt((x*self.velx)**2+(y*self.vely)**2):
            self.x += x*self.velx
            self.y += y*self.vely
        else: #To prevent overshoot
            self.x = location[0]
            self.y = location[1]
        
       #Make the boundaries of the bush an absolute reflective boundary
       #to ensure that the individual only moves within the bush
        
        right_boundary = self.bush.cent_x + 0.5*self.bush.bush_size
        left_boundary = self.bush.cent_x - 0.5*self.bush.bush_size
        upper_boundary = self.bush.cent_y + 0.5*self.bush.bush_size
        lower_boundary = self.bush.cent_y - 0.5*self.bush.bush_size

        if self.x > (right_boundary):
           self.x = right_boundary - (self.x-right_boundary)
           if self.velx > 0:
               self.velx *= -1
        
        if self.x < left_boundary:
           self.x = left_boundary + (left_boundary - self.x)
           if self.velx<0:
               self.velx *= -1
        
        if self.y > upper_boundary:
           self.y = upper_boundary - (self.y-upper_boundary)
           if self.vely>0:
               self.vely *= -1
        
        if self.y < lower_boundary:
           self.y = lower_boundary + (lower_boundary-self.y)
           if self.vely<0:
               self.vely *= -1
    
    def find_active_space(self): #For visualization purposes
        SPL = self.SPL
        return (20*10**((SPL-threshold_SPL)/20))
        

class Receiver: #Traditionally the female, this class represents the individuals which find signallers
    
    def __init__(self,x,y, velx, vely):
        
        '''
        x and y describe the position of the reciever in 2D space
        velx and vely describe the x and y components of its velocity respectively
        mov_prop describes the propensity of the receiver to move in any given timestep
        '''    
        
        #Position variables (in cm)
        self.x = x
        self.y = y
        self.bush = None #Which bush the individual is located in

        #Velocity variables (in cm/timestep)
        self.velx = velx
        self.vely = vely
        
        self.mating = False #To keep track of whether the female is currently mating
        self.mating_timer = 0 #To keep track of mating duration
        
        #Mated count
        self.mated_count = 0
        
        #Movement variables
        self.within_bush_steps = 0
        self.within_bush_distance = 0
        self.across_bush_steps = 0
        self.across_bush_distance = 0
        self.within_bush_phonotaxis_steps = 0
        self.within_bush_phonotaxis_distance = 0
        self.across_bush_phonotaxis_steps = 0
        self.across_bush_phonotaxis_distance = 0
        self.total_steps = 0
        self.total_distance = 0
        
        
	
    	#To store the type of male that the female mated with
        self.mated_male_type =[]

    def __key(self):

        '''
        Give each instance a key for unique identification
        Here, the key is based on location, velocity, and current mating status
        '''

        return (self.x,self.y,self.velx,self.vely,self.mating)
    

    def __eq__(self, other): 

        '''
        Define a way to compare two Receivers using their attributes
        (to find where an individual is in a set of individuals through a loop)
        '''

        if not isinstance(other, Receiver):

            # don't attempt to compare against unrelated classes
            return NotImplemented

        #compare them
        return self.__key() == other.__key()
       
    def dist(self,caller):
        xdist = self.x - caller.x
        ydist = self.y - caller.y
        
        return np.sqrt(xdist**2 + ydist**2) #Euclidean distance

    def listen(self,threshold_SPL): 
        
        '''Returns which callers are audible to the focal individual.'''
        
        '''Within bush'''
        callerlist = self.bush.callerlist

        closecallers = [] #We will add audible callers to this list
        SPLs = [] #We will add corresponding SPL values to this list
        for caller in callerlist:
            dist = self.dist(caller)
            if caller.calling and not caller.mating: #If the signaller is vocalizing and not mating
                if caller.decay(dist) >= threshold_SPL: #If the call is loud enough
                    #add to list
                    closecallers.append(caller)
                    SPLs.append(caller.decay(dist))
        
        '''Across bush'''
        close_bushes = []
        bush_dists = []
        bush_SPL = []
        adj_bushes = self.bush.adj_bushes

        #each element of adj_bushes is a tuple (bush,dist_to_bush)
        for bush in adj_bushes:
            close_bushes.append(bush[0])
            bush_dists.append(bush[1])
            bush_SPL.append(bush[0].bush_amp_decay(bush[1]))

        return closecallers, SPLs, close_bushes, bush_dists, bush_SPL
    
    def move(self,location): #location is a 2-tuple (loc_x,loc_y)

        '''
        this function implements actual movement towards a location based on 
        the velocity of the organism.
        '''
        
        #Find out where to go
        dist = np.sqrt((self.x - location[0])**2+(self.y - location[1])**2)
        
        if dist > 0:
            x,y = (location[0] - self.x)/dist , (location[1]-self.y)/dist #(x,y) is the unit vector pointing from self to location
        else:
            x,y = 0,0
            
        #Move according to your velocity
        
        if dist > np.sqrt((x*self.velx)**2+(y*self.vely)**2):
            self.x += x*self.velx
            self.y += y*self.vely
        else: #To prevent overshoot
            self.x = location[0]
            self.y = location[1]
        
       #Make the boundaries of the bush an absolute reflective boundary
       #to ensure that the individual only moves within the bush
        
        right_boundary = self.bush.cent_x + 0.5*self.bush.bush_size
        left_boundary = self.bush.cent_x - 0.5*self.bush.bush_size
        upper_boundary = self.bush.cent_y + 0.5*self.bush.bush_size
        lower_boundary = self.bush.cent_y - 0.5*self.bush.bush_size

        if self.x > (right_boundary):
           self.x = right_boundary - (self.x-right_boundary)
           if self.velx > 0:
               self.velx *= -1
        
        if self.x < left_boundary:
           self.x = left_boundary + (left_boundary - self.x)
           if self.velx<0:
               self.velx *= -1
        
        if self.y > upper_boundary:
           self.y = upper_boundary - (self.y-upper_boundary)
           if self.vely>0:
               self.vely *= -1
        
        if self.y < lower_boundary:
           self.y = lower_boundary + (lower_boundary-self.y)
           if self.vely<0:
               self.vely *= -1