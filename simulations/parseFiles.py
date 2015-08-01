import numpy as np
import csv
import os
import re

global resultDir
resultDir = "results/"

global summaryDir
summaryDir = "summary/"

global allmovesDir
allmovesDir = "allmoves/"

filename_all_moves = "iter_50_l_49_h_49_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.050_s_0.020_0.csv"
filename_summary = "iter_50_l_49_h_49_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.050_s_0.020_0.csv"


def parseFilename(rootFilename):
    '''Extract parameters from rootFilename'''
    fname = rootFilename.split("_")
    
    #print fname
    descList = [] 
    for i,value in enumerate(fname[0:-1:2]):
        #print i,value,fname[2*i+1]
        
        try:
            descList.append([value,fname[2*i+1],int(fname[2*i+1])])
        except ValueError:
            descList.append([value,fname[2*i+1],float(fname[2*i+1])])
        else:
            continue
    
    return descList

def makeFilename(descList,suffix=0):
    '''Construct filename from list of parameters as produced by "parseFilename" '''
    filename = "".join(["%s_%s_"%(item[0],item[1]) for item in descList]) + str(suffix) + ".csv"
    return filename 

def parseLine(line):
    '''parse one line of any allmoves file'''
    
    iter = int(line[0])
    
    if line[4] in ['M','FM','E','RM','RE']:
        strategy = int(line[9])
        deltaPayoff = float(line[10])
        distance = float(line[11])
        moveType = line[4]
        return {'iter' : iter, 'strategy' : strategy,'dPayoff' : deltaPayoff,'mDistance' : distance, "moveType": moveType}
    
    elif line[4] in ['U','R']:
        deltaStrategy = int(line[8]) - int(line[7])
        deltaPayoff = float(line[10]) - float(line[9])
        updateType = line[4]
        return {'iter' : iter,'dStrategy' : deltaStrategy,'dPayoff' : deltaPayoff,'updateType': updateType}
    else:
        print "error: " + line[4] + line 

def parseItems(itemDic,dstDic):
    
    for k,v  in itemDic.items():
        try:
            dstDic[k].append(v)
        except:
            dstDic[k] = [v]


def parseAllMoves(filename):
    '''Self documented'''
    M = {}
    U = {}
    codex = {'M': M, 'E':M,'FM':M,'RM':M,'RE':M,'U':U,'R':U}
       
    with open(resultDir + "allmoves/" + filename) as f:
        for l,line in enumerate(f):
            line = line[:-1].split(",")

            try:
                parseItems(parseLine(line),codex[line[4]])
            except:
                print line
                continue
                
    return {'M' : M,'U' :U}




def parseSummary(filename):
    '''Parse ONLY the final state'''
    with open(resultDir + "summary/" + filename) as f:
        for l,line in enumerate(f):
            line = line[:-1].split(",")

    fieldNames = ['iter','completion','coop_level','cooperators','defectors','empty']    
    summaryDic = {}
    
    
    for i,value in enumerate(line):           
        try:
            value = int(value)
        except ValueError:
            value = float(value)
        else:
            pass
        summaryDic[fieldNames[i]] = value
    
    return summaryDic
    
      
def parseAll(filename):

    ##summaryPath = resultDir + summaryDir + filename
    ##allmovesPath = resultDir + allmovesDir +  filename

    #print allmovesPath

    descDic = parseFilename(filename[:-6]) 
    moves = parseAllMoves(filename)
    
    summaryDic = parseSummary(filename)
    return {'summary': summaryDic, 'M' : moves['M'], 'U' :moves['U']}
    
def listRootFilenames():
    listdir = os.listdir(resultDir + allmovesDir)
    
    rootFiles = []
    
    for l in listdir[1:]:
        rootFiles.append(l[:-6])
        
    return list(np.unique(rootFiles))



