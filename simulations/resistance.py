import boto
import numpy as np
import pylab as pl
import json,zlib
from datetime import datetime
import os
from operator import itemgetter

bucketName = "pgame"
resultDir = "results"
s3 = boto.connect_s3()
global bucket
bucket = s3.get_bucket(bucketName)

fig_width_pt = 420.0  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0 / 72.27  # Convert pt to inch
golden_mean = (np.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
fig_width = fig_width_pt * inches_per_pt  # width in inches
fig_height = fig_width  # *golden_mean      # height in inches
fig_size = [fig_width, fig_height]


params = {'backend': 'ps',
          'axes.labelsize': 25,
          'text.fontsize': 32,
          'legend.fontsize': 14,
          'xtick.labelsize': 20,
          'ytick.labelsize': 20,
          'text.usetex': False,
          'figure.figsize': fig_size}
pl.rcParams.update(params)


rootDir = '/Users/maithoma/work/compute/pgames_resistance/'

highCoopKeys = ['iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0100_0_d037e.json.zlib',
               'iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0200_0_10c4d.json.zlib',
               'iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0300_3_2f65d.json.zlib',
               'iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0400_0_99a70.json.zlib',]

failedCoopKeys = ['iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0370_3_5acd8.json.zlib',
                  'iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0380_0_16bd4.json.zlib',
                  'iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0420_1_7a3b5.json.zlib',
                  ]

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


def retrieveGrid(key,iter = -1,save=False):
    
    
    
    key = bucket.get_key("results/" + key)
    J = json.loads(zlib.decompress(key.get_contents_as_string()))
    
    grids = J['grids'].split("\n")
    
    
    if iter == -1:
        grid = J['grids'].split("\n")[-2].split(":")[1][1:-1]
    else:
        for g in grids:
            line = g.split(":")
            if i== int(line[0]):
                grid = line[1][1:-1]
                break
    
    
    if save:
        f = open("grid.csv",'wb')
        f.write(grid)
        f.close()
    
    return grid


def retrieveSimul(key):
    
    key = bucket.get_key("results/" + key)
    dic = json.loads(zlib.decompress(key.get_contents_as_string()))
    return dic

'''
def coopLevel(dic):
    
    iter = []
    coop = []
    
    lines = dic['summary'].split("\n")
        
    for line in lines[1:-1]:
        iter.append(float(line.split(",")[0]))
        coop.append(float(line.split(",")[2]))
    
    
    return iter,coop
''' 
   
def coopLevel(filename):
    
    iter = []
    coop = []
    
    lines = open(rootDir  + "results/summary/" + filename).read().split("\n")
    
            
    for line in lines[1:-1]:
        iter.append(float(line.split(",")[0]))
        coop.append(float(line.split(",")[2]))
    
    return iter,coop 


    
def formatCommand(variableNames,values, configFile="pgame.cfg",grid=False):
    command = "pgames " + "".join(["-%s %s "%(variableNames[i],values[i]) for i in range(len(variableNames))])
    command = command + " -c %s"%configFile
    if grid:
        command = command + " -g grid.csv"
    return command 

def processHighCoop(repeat=1, dryRun=True):
    counter = 0
    for key in highCoopKeys:
        sMin = float(parseFilename(key)['s'])
        #retrieveGrid(key,iter = -1,save=True)
        print key


        #for i,s in enumerate(np.arange(sMin,0.11,0.005)):
        for i,s in enumerate(np.arange(0.043,0.062,0.002)):
            n = 0
            while n < repeat:
                n += 1
                counter += 1
                command = "pgames " + " -g grid.csv" + " -c pgame.cfg" + " -s %s"%s	
                print counter,i, "command: ", command, "  " , datetime.now()

                if dryRun:
	               continue
                os.system(command)


def makeListResistanceSims(repeat):

    iter = [0.01,0.02,0.03,0.04,]
    dic = {}

    for i,ix in enumerate(iter):
        dic[ix] = list(repeat*i + np.arange(0,repeat))

    return dic
        
def plotResistance():
    
    dic = makeListResistanceSims(3)
    
    pl.close("all")
    
    colors = []
    
    for k,key in enumerate(np.sort(dic.keys())):
        pl.figure(k,(11,7))
        pl.title("starting property violation: %s"%key)
        
        
        low = 0
        high = 0
        
        if rootDir == '/Users/maithoma/work/compute/pgames_resistance/':
            range = np.arange(key,0.11,0.005)
            iter = 2000
             
        elif rootDir == '/Users/maithoma/work/compute/pgames_resistance2/':
            range = np.arange(0.043,0.062,0.002)
            iter = 4000
                
        color = np.linspace(0.7,0.3,len(range))
    
        for i,s in enumerate(range):
            for j,jx in enumerate(dic[key]):
                
                if j==0:
                    label = str(s)
                elif j>0:
                    label = '_nolegend_'
                    
                
                filename = 'iter_%s_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_%.4f_%s.csv'%(iter,s,jx)
                print filename     
                #if s < 0.04 or s > 0.065:
                #    continue
                
                try:
                    x,y = coopLevel(filename)
                    #print key,i,jx,s,y[-1],filename
                    if float(y[-1]) < 0.7:
                        pl.semilogx(x,y,alpha=1,lw= 1.,label=label,color=[color[i],color[i],1])
                        #pl.semilogx(x,y,alpha=1,lw= 1.,label=label,color='c')
                        low +=1
                    elif float(y[-1]) > 0.7:
                        pl.semilogx(x,y,alpha=1,lw= 1.,label=label,color=[color[i],1,color[i]])
                        #pl.semilogx(x,y,alpha=1,lw= 1.,label=label,color='m')
                        high +=1
                except:
                    continue

        #pl.text(100000,0.85,"high:%s \n low:%s"%(high,low))       
        pl.legend(loc=0)
        pl.xlabel("Iterations (log10)")
        pl.ylabel("Cooperation Level")
        pl.xlim(xmax=5*10**8)
        pl.ylim(0.,1)
        
   
def saveFromCollapse(repeat=1,dryRun = True):
    ''' Choose file with defectors winning with all intermediary grids'''
    rootDir = '/Users/maithoma/work/compute/pgames_adaptation/'
    filename = "iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0420_0.csv"    
    sBase = 0.042
    
    
    '''Open Summary File'''
    summaries = open("%sresults/summary/%s"%(rootDir,filename),'rb').read().split("\n")
    nGrids = len(summaries)
    print nGrids
    '''Open grid file'''
    grids = open("%sresults/grids/%s"%(rootDir,filename),'rb').read().split("\n")

    counter = 0

    for i,ix in enumerate(-np.arange(35,nGrids,35)):
        
        summary = summaries[ix].split(",")

        if float(summary[2]) < 0.25:
            continue
        
        iteration = grids[ix].split(":")[0]
        grid = grids[ix].split(":")[1][1:-2]
        
        '''save grid'''
        f = open(rootDir + "grid.csv",'wb')
        f.write(grid)
        f.close()
        
        #for s in np.arange(sBase-0.005,0.02,-0.005):
        for perc in [0.85,0.95]:
            s = sBase*(1-perc)
            n = 0
            while n < repeat:
                n += 1
                counter += 1
                command = "pgames " + " -g grid.csv" + " -c pgame.cfg" + " -s %s"%s    
                print counter,i, "command: ", command, "  " , datetime.now()

                if dryRun:
                    continue
                os.system(command)
        
        print i,ix,iteration,summary[0],summary[2],len(grid)
    


def triggerCollapse(repeat=1,dryRun = True):
    ''' Choose file with defectors winning with all intermediary grids'''
    rootDir = '/Users/maithoma/work/compute/pgames_resistance3/'
    filename = "iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0370_0.csv"    
    sBase = 0.037
    
    
    '''Open Summary File'''
    summaries = open("%sresults/summary/%s"%(rootDir,filename),'rb').read().split("\n")
    nGrids = len(summaries)
    print nGrids
    '''Open grid file'''
    grids = open("%sresults/grids/%s"%(rootDir,filename),'rb').read().split("\n")

    counter = 0

    for i,ix in enumerate(map(int,-np.linspace(35,nGrids-35,15))):
        
        summary = summaries[ix].split(",")

        if float(summary[2]) < 0.25:
            continue
        
        iteration = grids[ix].split(":")[0]
        grid = grids[ix].split(":")[1][1:-2]
        
        '''save grid'''
        f = open(rootDir + "grid.csv",'wb')
        f.write(grid)
        f.close()
        
        for s in np.arange(sBase + 0.001,0.045,0.002):
        #for perc in [0.85,0.95]:
            #s = sBase*(1-perc)
            n = 0
            while n < repeat:
                n += 1
                counter += 1
                command = "pgames " + " -g grid.csv" + " -c pgame.cfg" + " -s %s"%s    
                print counter,i, "command: ", command, "  " , datetime.now()

                if dryRun:
                    continue
                os.system(command)
        
        print i,ix,iteration,summary[0],summary[2],len(grid)
    

def binning(x,y,bins,log_10=False,confinter=5):
    from numpy import log10,linspace,logspace,mean,median,append,std,array
    from scipy.stats import scoreatpercentile
    #print bins

    x = np.array(x)
    y = np.array(y)

    if isinstance(bins,int) or isinstance(bins,float):
        if log_10:
            c = (x > 0)
            bins = logspace(np.log10(min(x[c]))*0.9,np.log10(max(x[c]))*1.1,bins)
        else:
            bins = linspace(min(x)*0.9,max(x)*1.1,bins)
        

    
    if log_10:
        c = (x > 0)*(y > 0)
        x = x[c]
        y = y[c]
        bins = np.log10(bins)
        x = np.log10(x)
        y = np.log10(y)

    Tbins =[]
    Median =[]
    Mean = []
    Sigma =[]
    Perc_Up =[]
    Perc_Down = []
    Points=[]

    for i,ix in enumerate(bins):
        #print i,ix
        if i+2>len(bins):
            break
        
        c1 = x >= ix
        c2 = x < bins[i+1]
        c=c1*c2
        
        if len(y[c])>0:
            Tbins = append(Tbins,median(x[c]))
            Median =  append(Median,median(y[c]))
            Mean = append(Mean,mean(y[c]))
            Sigma = append(Sigma,std(y[c]))
            Perc_Down = append(Perc_Down,scoreatpercentile(y[c],confinter))
            Perc_Up = append(Perc_Up,scoreatpercentile(y[c],100-confinter))
            Points = append(Points,len(y[c]))
                    
        Perc_Up = array(Perc_Up)
        Perc_Down = array(Perc_Down)
    
    return {'bins' :Tbins, 'median' :Median , 'mean' : Mean, 'sigma' : Sigma, 'percDown' : Perc_Down, 'percUp' : Perc_Up,'nPoints': Points}



    