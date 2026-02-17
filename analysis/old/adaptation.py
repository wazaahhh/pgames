import numpy as np
import pylab as pl
from datetime import datetime
import os


global rootDir
rootDir = '/Users/maithoma/work/compute/pgames_adaptation/'
originFile = 'iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0420_0.csv'


def coopLevel(filename):
    
    iter = []
    coop = []
    
    lines = open(rootDir  + "results/summary/" + filename).read().split("\n")
    
            
    for line in lines[1:-1]:
        iter.append(float(line.split(",")[0]))
        coop.append(float(line.split(",")[2]))
    
    
    return iter,coop

def makeListAdaptationSims():
    iters = [597596,552023,512308,477438,434862,397996,359501,322381,283961,252854,222303,194493,161555,131440,105668,82147,58511,40507,21135,12924]

    dic = {}

    for i,ix in enumerate(iters):
        dic[ix] = list(3*i + np.array([0,1,2]))

    return dic


def plotAdaptations():
    
    pl.close("all")
    #pl.figure(1,(13,7))
    #x,y = coopLevel(originFile)
    #pl.semilogx(x,y,'k-',lw=2)

    dicList = makeListAdaptationSims()
    
    
    sBase= 0.042
    sList = np.arange(sBase-0.005,0.02,-0.005)
    sList = np.append(sList,[0.0105,0])
    
    
    for k,key in enumerate(np.sort(dicList.keys())):
        for i,ix in enumerate(dicList[key]):
            for j,jx in enumerate(sList):
                
                
                filename = 'iter_2000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_%.4f_%s.csv'%(jx,ix)
                                
                pl.figure(j,(10,8))
                pl.title("new s=%s (%.2f perc)"%(jx,(jx-sBase)/sBase*100))
                pl.xlabel("iterations")
                pl.ylabel("cooperation level")
                x,y = coopLevel(originFile)
                pl.semilogx(x,y,'k-',lw=2)
                
                x,y = coopLevel(filename)
                      
                if float(y[-1]) == 0:
                    pl.semilogx(np.array(x) + float(key),y,'m-',lw=0.4)
                    yIter = np.linspace(0,1,10)
                    xIter = np.zeros_like(yIter) + float(key) 
                    pl.semilogx(xIter,yIter,'r-',lw=4,alpha=0.1)
                    

                elif float(y[-1]) > 0:
                    pl.semilogx(np.array(x) + float(key),y,'c-',lw=0.4)
                    yIter = np.linspace(0,1,10)
                    xIter = np.zeros_like(yIter) + float(key)
                    pl.semilogx(xIter,yIter,'b-',lw=4,alpha=0.1)
                
                print jx,"%.2f"%((jx-sBase)/sBase),y[-1]