The majority of the files in this directory are MATLAB files. 

Eventually, these will be either ported to Python or called by a Python function. They are currently in this folder because they are relevant to the relay station, but some of the files will not actually be run on the relay station.

The files that are most relevant:

teager.m: Calculates the Teager energy of the input signal (from mic)
winAvg.m: Calculates a windowed average of the input signal
TimeIdentifier.m: Finds all times above a threshold, flags those times with a 1, and makes all other times have value of 0
FiveSecEnvProcessor.m: The overall script that calls all the other functions and generates a result
