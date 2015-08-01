import os
import numpy as np
from datetime import datetime

constants = {}

variables = {"M" : [1,3,5,7],
             'd' : list(np.linspace(0.3,0.9,7)),
             's' : [0] + list(np.linspace(0.005,0.050,10))}

#variables = {"M" : [1],
#             'd' : list(np.linspace(0.1,0.2,2)),
#             's' : [0] + list(np.linspace(0.005,0.050,10))}

variables = {"M" : [1],
             'd' : list(np.linspace(0.3,0.9,7)),
             's' : [0] + list(np.linspace(0.055,0.10,10))}


variableNames = ['M','d','s']

def formatCommand(variableNames,values):
    command = "./abm " + "".join(["-%s %s "%(variableNames[i],values[i]) for i in range(len(variableNames))])
    return command 


def simul(dryRun=False):
    counter = 0
    for i,ix in enumerate(variables['M']):
        for j,jx in enumerate(variables['d']):
            for k,kx in enumerate(variables['s']):
                counter  += 1
                command = formatCommand(variableNames,[ix,jx,kx])
                print counter,ix,jx,kx, "command: ", command, "  " , datetime.now()
                if dryRun:
                    continue
                os.system(command)