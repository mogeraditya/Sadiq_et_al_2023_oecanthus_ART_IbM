#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Shikhara Bhat
Email ID: shikharabhat@gmail.com
Date created: 2021-12-19 14:42:08
Date last modified: 2022-01-09 20:20:59
Purpose: The landscape where the simulatiosn take place
this is a series of bushes and distances between them
'''

import numpy as np
import random as rd
from class_male_and_female import Receiver, Signaller
from class_bush import Bush
from static_params import threshold_bush_dist

def bush_dist(bush1,bush2):
        '''
        Get the euclidean distance between two bushes
        the distance between two bushes is defined here as
        the distance between their centers
        '''
        return(np.sqrt((bush1.cent_x-bush2.cent_x)**2 + (bush1.cent_y-bush2.cent_y)**2))


class Landscape:

    def __init__(self,xdims,ydims):

        #Size parameters
        #xdims and ydims are lists of the form [min,max,step]
        #and specify the dimensions of the entire simulation
        self.xdims = xdims
        self.ydims = ydims

        #Only needed for plotting purposes
        self.xvals = np.arange(self.xdims[0],self.xdims[1]+self.xdims[2],self.xdims[2])
        self.yvals = np.arange(self.ydims[0],self.ydims[1]+self.ydims[2],self.ydims[2])


        #bush information
        #will be filled in using other functions later
        self.bushlist = []
        self.bushcenters = []
        self.bushdists = []

    
    def make_bushes(self,bush_dens,bush_size_mean,bush_size_sd):

        '''
        Fill in the landscape with bushes. Bushes are assumed to be distributed
        according to a uniform random 2D distribution. Bush sizes are assumed to 
        follow a Normal distribution with specified mean and variance 
        (both of these can be changed to other distributions later if required)
        '''
        #compute area of the landcscape in square meters
        #the 10^-4 is to convert from sq cm to sq m
        landscape_area = (self.xdims[1]-self.xdims[0])*(self.ydims[1]-self.ydims[0])*(10**-4)
        
        num_bushes = int(round(bush_dens*landscape_area))

        #spatial locations - drawn from uniform random 2D distribution
        x_locs = np.random.uniform(self.xdims[0],self.xdims[1],size=num_bushes)
        y_locs = np.random.uniform(self.ydims[0],self.ydims[1],size=num_bushes)

        #bush sizes - drawn from truncated Normal distribution
        bush_sizes = np.zeros((0,)) #empty list to fill below
        while bush_sizes.shape[0] < num_bushes:
            sample = np.random.normal(bush_size_mean,bush_size_sd,size=(num_bushes,))

            #only accept those samples which are non-negative
            accepted = sample[sample>0]
            bush_sizes = np.concatenate((bush_sizes,accepted),axis=0)
        bush_sizes = bush_sizes[:num_bushes] #discard extra values

        bush_sizes = list((bush_sizes).flatten())

        for i in range(num_bushes):

            #make the bushes
            bush = Bush(x_locs[i],y_locs[i],bush_sizes[i])

            #add to list
            self.bushlist.append(bush)
            self.bushcenters.append((x_locs[i],y_locs[i]))
    
    def make_distance_list(self):

        '''
        To reduce computational complexity, we will compute
        all inter-bush distances at the beginning and store
        these results 
        (so that we don't need to recompute at each step)
        '''

        for bush in self.bushlist:
            for otherbush in self.bushlist:
                dist = bush_dist(bush,otherbush)
                if dist < threshold_bush_dist and dist > 0: #If the bushes are not too far away from each other

                    #Remember the bushes and distances
                    bush.adj_bushes.append((otherbush,dist))
                    #otherbush.adj_bushes.append((bush,dist))
    
    def assign_locations(self,obj):

        '''
        this function assigns the obj an x and y coordinate that is
        within one of the bushes present in the landscape. The obj 
        MUST contain x and y attributes for this to work. We will use
        this to assign random locations to callers and receivers.
        '''

        #Pick a random bush
        rand_bush = rd.choice(self.bushlist)

        #Assign the object a random location within the bush
        rand_bush.assign_locations_in_bush(obj)
        if isinstance(obj,Signaller):
            rand_bush.callerlist.append(obj)
        elif isinstance(obj,Receiver):
            rand_bush.receiverlist.append(obj)
        else:
            return NotImplementedError

        #Make sure the object remembers which bush it is in
        obj.bush = rand_bush

