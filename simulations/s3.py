import boto
import zlib
import json
import re
import uuid
from operator import itemgetter

from parseFiles import *


bucketName = "pgame"
resultDir = "results"
s3 = boto.connect_s3()
global bucket
bucket = s3.get_bucket(bucketName)


def uploadJson(rootDir,filename):
    
    try:
        keyname = makeKey(rootDir,filename)
        payload = pullTogether(rootDir,filename)
    
        key = bucket.new_key(keyname)
        key.set_contents_from_string(payload)
        print filename, "=> uploaded."
    except:
        print "could not upload: %s"%keyname 


def getJson(keyname):
    key = bucket.get_key(keyname)
    data = key.get_contents_as_string()
    return json.loads(zlib.decompress(data))


def makeKey(rootDir,filename):
    descDic = parseFilename(filename)
    token = str(uuid.uuid4())[-5:]
    key = "%s/%s_%s.json.zlib"%(resultDir,filename[:-4],token)
    return key

def pullTogether(rootDir,filename, compress=True):
    
    J = {}
    
    for dataType in ['summary','allmoves','grids']:
        path = "%sresults/%s/%s"%(rootDir,dataType,filename)
        #print dataType,path
        
        data = open(path,'rb').read()        
        
        J[dataType] = data
        
    if compress:
        return zlib.compress(json.dumps(J))
    else:
        return J


def prepareForViz(rootDir,filename,loadFromS3=False):

    

    if loadFromS3:
        #load from S3
        pass
    else:
        #load data from local file
        J = pullTogether(rootDir,filename, compress=False)
    
    #format input
    J['input'] = parseFilename(filename)
    #format moves
    
    moves = []
    L = []
    iter_old = 0
    
    for i,mv in enumerate(J['allmoves'].split("\n")):
        mv  = mv.split(",")
        
        
        if not len(mv) in [11,12]:
            continue
        
        iter = int(mv[0])
        
        if iter > iter_old:
            moves.append(L)
            L = []
            for j in range(iter - iter_old - 1):
                moves.append([])
        
        
        if mv[4] in ['U','R']:
            get_items = itemgetter(5,6,8)
            L.append(map(int,list(get_items(mv))))
            #print L
        
        elif mv[4] in ['M','FM','E','RE','RM']:
            get_items = itemgetter(5,6)
            mv_out = list(get_items(mv))
            mv_out.append('-1')
            mv_in = list(itemgetter(7,8)(mv))
            mv_in.append(mv[9])
            L.append([map(int,mv_out),map(int,mv_in)])
            #print L
        
        
        
        #print moves[-1]

        iter_old = iter
    moves.append(L)   
    J['mv'] = moves
    #format grids
    grids = {}
    for iter,grid in re.findall("(.*?):(\[.*?\])",J['grids']):
        grids["t" + iter] = grid[1:-2].split(",")
    
    J['grids'] = grids

    return J

def parseFilename(filename):

    fname = filename.split("_")
    n = fname[-1][:-4]
    fname[-1] = "n"
    fname.append(n)
    
    
    descList = [] 
    for i,value in enumerate(fname[0:-1:2]):
        #print i,value,fname[2*i+1]      
        try:
            descList.append([value,fname[2*i+1],fname[2*i+1]])
        except ValueError:
            descList.append([value,fname[2*i+1],fname[2*i+1]])
        else:
            continue
    
    
    descDic = dict(zip(*[zip(*descList)[0],zip(*descList)[2]]))
    descDic['n'] = n
    
    return descDic

def getAllSummaries(save=True):
    
    rootDirs = ['/Users/maithoma/work/compute/pgames_dAll_transition/',
                '/Users/maithoma/work/compute/pgames_dAll2_transition',
                '/Users/maithoma/work/compute/pgames_d02_transition/',
                '/Users/maithoma/work/compute/pgames_d03_transition/',
                '/Users/maithoma/work/compute/pgames_d04_transition/',
                '/Users/maithoma/work/compute/pgames_d05_transition/',
                '/Users/maithoma/work/compute/pgames_d06_transition/',
                '/Users/maithoma/work/compute/pgames_d07_transition/',
                '/Users/maithoma/work/compute/pgames_d08_transition/',
                ]
    
    outlist = []
    
    for rd in rootDirs:
        listDir = os.listdir(rd+ "results/summary/")
        for filename in listDir:
            path = "%sresults/summary/%s"%(rd,filename)
            #print filename
            #if filename == ".DS_Store":
            #    continue
            
            descDic = parseFilename(filename)
            
            if not descDic.has_key('iter') or descDic['iter'] < 1000:
                continue

            data = open(path,'rb').read()
            
            outdata = []
            
            for line in data.split("\n")[:-1]:
                outdata.append(line.split(","))
            
            outlist.append({'input': descDic, 'summary': outdata})
    
    if save:
        print "compressing and saving locally"
        J = zlib.compress(json.dumps(outlist))
        f = open("summary_all.json.zlib",'wb')
        f.write(J)
        f.close()
        
    return outlist
    

def bulkUpload(rootDir):
    listDir = os.listdir(rootDir + "results/summary/")
    for filename in listDir:
        uploadJson(rootDir,filename)
        
