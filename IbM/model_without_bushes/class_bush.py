#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Shikhara Bhat
Email ID: shikharabhat@gmail.com
Date created: 2021-12-18 18:51:45
Date last modified: 2021-12-29 11:24:02
Purpose: Implement bushes into the model

Broad idea:
Each bush will play the role that the grid class played in the model with no spatial structure
Each bush is coarse-grained to have a single 'mean amplitude' that the female listens to
we would want the following broad structure (GUESS):
1) FEMALES probabilistically move from their current bush to adjacent bushes according to the 
amplitude difference between their current bush and the adjacent bushes. We need a preference function for this.
2) MALES probabilistically move from their current bush to adjacent bushes according to the
time since last mating. Alternatively, we could have males not move at all between bushes. 
'''

import random as rd
import numpy as np
from numpy.lib.arraysetops import isin

from class_male_and_female import Receiver, Signaller

class Bush:

    def __init__(self,cent_x,cent_y,bush_size):

        #spatial params
        #A bush is a square of a specified size centered at a specified location
        
        self.cent_x = cent_x #x coordinate of the center, in cm
        self.cent_y = cent_y #y coordinate of the center, in cm
        self.bush_size = bush_size #length of the side of the bush, in cm
        self.adj_bushes = [] #bushes which are close to a focal bush. We will fill this in later

        #inhabitants of the bush
        #we will fill these lists when running the model
        self.callerlist = [] #males
        self.receiverlist = [] #females

        self.bush_amp = 0 #mean amplitude of the bush (in dB SPL)

    def update_mean_amp(self): #update the mean amplitude of the bush at each instant

        num_callers = len(self.callerlist)
        if num_callers:
            loudness = 0
            for caller in self.callerlist:
                if caller.calling:
                    loudness += 10**(caller.SPL/20) #since dB is logarithmic, adding should be done in Pa
            
            self.bush_amp = 20*np.log10(loudness) #convert back to dB
        else:
            self.bush_amp = 0

    def bush_amp_decay(self,dist):

        '''
        Function describing how the call decays with distance. Can be modified as required.
        We currently assume spherical spreading for simplicity. The 'average amplitude' of
        the bush is taken to emanate from the center of the bush for simplicity.
        '''
            
        if dist > 0:
            
            TL = 20*np.log10(dist/20) #I'm assuming source SPL was measured at a distance of 20cm from the cricket (standard distance for these kind of measurements)
            return self.bush_amp - TL
        
        else:
            return self.bush_amp
    
    def within_bush(self,x,y):
        
        '''
        Find out whether a given object with a spatial location is
        within the focal bush or not
        '''
        
        #check if (x,y) is within the square. If side of the square is a,
        #we need x to be between x_center - a/2 and x_center + a/2
        #and y to be between y_center - a/2 and y_center + a/2
        if (self.cent_x - self.bush_size/2 <= x) and (self.cent_x + self.bush_size/2 >= x) and (self.cent_y - self.bush_size/2 <= y) and (self.cent_y + self.bush_size/2 >= y):
            return True
        else:
            return False


    def assign_locations_in_bush(self,obj=None):
        
        '''
        when given an object, this function assigns the obj an x and y
        coordinate that is within the focal bush. The obj MUST contain 
        x and y attributes for this to work. We will use this to assign 
        random locations within the bush to callers and receivers.

        When not given an object, the function instead returns a random
        and y value that is within the bush. We will use this to program
        random movement within a bush
        '''
        
        accept_values = False
        while not accept_values:

            #pick an x and y coordinate randomly
            rand_x = rd.uniform(self.cent_x-self.bush_size,self.cent_x+self.bush_size)
            rand_y = rd.uniform(self.cent_y-self.bush_size,self.cent_y+self.bush_size)

            #check if this point is within the bush
            #If the point is within the bush, accept these x and y values
            accept_values = self.within_bush(rand_x,rand_y)
        
        if obj is not None:
            obj.x = rand_x
            obj.y = rand_y
        else:
            return rand_x,rand_y

    def find_cricket_index(self,obj):
        
        '''
        Find out where in the list of callers/receivers a given caller/receiver 
        (specified by the obj argument) is located.
        '''
        
        if isinstance(obj,Signaller):
            focal_list = self.callerlist
        elif isinstance(obj,Receiver):
            focal_list = self.receiverlist
        else:
            return NotImplementedError
        
        for i in range(len(focal_list)):
            if focal_list[i] == obj:
                return i
        
        return None

    



