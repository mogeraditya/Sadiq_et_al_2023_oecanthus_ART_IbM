Each individual folder implements a separate version of the IbM - One with bushes, and one without. Both are meant to be run from the terminal, ideally on some sort of cluster computer. In both cases, to run the simulation, simply run

```zsh
foo@bar:~ python3 main_array_run.py -f $FREQ -d $DENS -file $FILENAME
```

on a terminal. In this line,

* The ```-f``` flag (which was provided the argument ```$FREQ``` above) should receive a float in the interval [0,1], and specifies the trait frequency of the baffling tactic.
* The ```-d``` flag (which was provided the argument ```$DENS``` above) should receive a positive float, and specifies the population density of crickets.
* The ```-file``` flag (which was provided the argument ```$FILENAME``` above) should receive a string, and specifies the filename of the .CSV file in which output of the IbM should be stored.
</br>
</br>
In both cases, the output of the IbM will be a .CSV file containing several relevant output variables, most importantly, the mating success of each tactic. To run several instances of the IbM in parallel, simply write a bash script that loops through several values of baffling trait frequency and/or population density and runs ```main_array_run.py``` with each set of parameters. 

  

