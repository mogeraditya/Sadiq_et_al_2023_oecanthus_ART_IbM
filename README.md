# Individual-based model of alternative reproductive tactics in *Oecanthus henryi* (an Indian tree cricket species)

This repository contains scripts used in Sadiq, Bhat, <i>et al.</i> 2023. The associated manuscript can be found on biorxiv at this link.

## Problem statement and goals
Males of the tree cricket *Oecanthus henryi* use one of three distinct alternative reproductive tactics (ARTs) to obtain mates:

* Bafflers construct an acoustic structure called a 'baffle' using leaves and call from within this baffle. The baffle increases the amplitude of their calls.
* Callers simply call from perches to attract mates. The amplitude of the call of a caller is less than that of a baffler.
* Silent males do not call at all, and simply wait silently for females.
 
Females perform phonotaxis to find mates, and females are known to often preferentially move towards louder males. The code in this repository implements an individual-based model (IbM) in Python to accurately simulate the dynamics of *Oecanthus henryi* on a single-night timescale, with the goal of looking at the fitnesses of these three ARTs (quantified by mating success) over ecological timescales.

## Guide to the repo

* the *IbM* folder contains all Python files that are used for running simulations, and implements the IbMs used in the paper. We implemented two different models, one with bushes and one with a spatially homogeneous habitat, and these can be found in two different sub-folders.
* the *figurewise_plotting* folder contains R scripts to replicate the figures presented in Sadiq et al 2023, as well as the data files that were used to create the plots (obtained as output of the IbM).


