import numpy as np
import csv
import os
import re

global resultDir
resultDir = "/Users/maithoma/work/compute/pgames_d05_transition/results/"

global summaryDir
summaryDir = "summary/"

global allmovesDir
allmovesDir = "allmoves/"


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
    
    
    descDic = dict(zip(*[zip(*descList)[0],zip(*descList)[2]]))
    
    return {'descList' : descList, 'descDic' : descDic}

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
    #M = {}
    #U = {}

    outdic = {'M': {}, 'E': {},'FM':{},'RM':{},'RE':{},'U':{},'R':{}}
    
    with open(resultDir + "allmoves/" + filename) as f:
        for l,line in enumerate(f):
            line = line[:-1].split(",")

            try:
                parseItems(parseLine(line),outdic[line[4]])
            except:
                print line
                continue
                
    return outdic




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
        rootFiles.append(l[:79])
        
    return list(np.unique(rootFiles))


def selectRootFilenames(descDic):
    '''Selects root files of interest according to input dictionary'''
    
    fname_rt = listRootFilenames()
    
    list_rt = []
    
    varDic = {}
    
    for rt in fname_rt:
        k=0
        dic = parseFilename(rt)['descDic']
        for item in dic.items():
            if descDic.has_key(item[0]) and descDic[item[0]] == item[1]:
                k+=1
                
            elif not descDic.has_key(item[0]):
                try:
                    varDic[item[0]].append(item[1])
                except:
                    varDic[item[0]] = [item[1]]

        if k==len(descDic):
            list_rt.append(rt)
            
    for k,v in varDic.items():
        varDic[k] = list(np.sort(np.unique(v)))
        
    return {'list_rt':list_rt, 'var_dic': varDic}