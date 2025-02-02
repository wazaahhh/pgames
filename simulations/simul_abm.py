import os
import numpy as np
from datetime import datetime

constants = {}

variables = {"M" : [9],
             'd' : list(np.linspace(0.7,1,4)),
             's' : [0]} #  + list(np.linspace(0.005,0.060,12))


#variables = {"M" : [1,2,3,5,7,9],
#             'd' : list(np.linspace(0.1,1,10)),
#             's' : [0] + list(np.linspace(0.005,0.060,12))}


variableNames = ['M','d','s']

def formatCommand(variableNames,values, configFile="pgame.cfg"):
    command = "./abm " + "".join(["-%s %s "%(variableNames[i],values[i]) for i in range(len(variableNames))])
    command = command + " -c %s"%configFile
    return command 


def simul(configFile="pgame.cfg",dryRun=False):
    counter = 0
    for i,ix in enumerate(variables['M']):
        for j,jx in enumerate(variables['d']):
            for k,kx in enumerate(variables['s']):
                counter  += 1
                command = formatCommand(variableNames,[ix,jx,kx],configFile=configFile)
                print counter,ix,jx,kx, "command: ", command, "  " , datetime.now()
                if dryRun:
                    continue
                os.system(command)