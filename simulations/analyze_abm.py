from parseFiles import *
import pylab as pl
import numpy as np



def cooperationLevel(descDic):
    '''find cooperation level from simulations with parameters provided in descDic'''
    rt_fnames = selectRootFilenames(descDic)['list_rt']
    rt_variables = selectRootFilenames(descDic)['var_dic']
    
    M = []
    d = []
    s = []
    coopLevel = []
    meanMigration = []
    meanDeltaPayoff = []
    finalIter = []
    
    for rt in rt_fnames:
        try:
            description = parseFilename(rt)
            #dList = parseFilename(rt)['descList']
            #description = descriptiont(zip(*[zip(*dList)[0],zip(*dList)[2]]))
            M.append(description['descDic']['M'])
            d.append(description['descDic']['d'])
            s.append(description['descDic']['s']),
        
            filename = makeFilename(description['descList'])
            coopLevel.append(parseSummary(filename)['coop_level'])
            finalIter.append(parseSummary(filename)['iter'])
        except:
            print rt
            continue
        
    return {'M' : M , 'd' : d , 's' :s , 'coopLevel' : coopLevel, 'finalIter' :  finalIter, 'variables' : rt_variables}


def aggregates(filename,display=False):
    
    outdic = {}
    outdic['desc'] = parseFilename(filename[:-6])['descDic']
    parsed = parseAllMoves(filename)
    
    for k,dic in parsed.items():
        for key,value in dic.items():
            
            if key == "iter":
                value = np.diff(value)
                try: 
                    try:
                        outdic[k][key] =  {'mean' : np.mean(value), 'std' : np.std(value),'tseries' : list(value)}
                    except:
                        outdic[k] = {key : {'mean' : np.mean(value), 'std' : np.std(value),'tseries' : list(value)}}                
                    
                    if display: print k,key,np.mean(value),np.std(value)
                except:
                    #print k,key
                    continue
            else:
                try: 
                    try:
                        outdic[k][key] =  {'mean' : np.mean(value), 'std' : np.std(value),'tseries' : {'iter' : dic['iter'], 'values' : list(value)}}
                    except:
                        outdic[k] = {key : {'mean' : np.mean(value), 'std' : np.std(value),'tseries' : {'iter' : dic['iter'], 'values' : list(value)}}}       
                    if display: print k,key,np.mean(value),np.std(value)
                except:
                    #print k,key
                    continue
    return outdic

def showPayoffAggregates(descDic):
    rt_fnames = selectRootFilenames(descDic)['list_rt']
    
    meanPayoffs = {'s' : [], 'd' :[], 'migration' : []}
    
    for rt in rt_fnames:
        agg = aggregates(rt + "_0.csv")
        desc = agg.pop('desc')
        
        meanPayoffs['s'].append(desc['s'])
        meanPayoffs['d'].append(desc['d'])
        meanPayoffs['migration'].append(desc['M'])

        #print "  " + str(desc['s']) + ",".join([" %s:%.2f"%(k,v['dPayoff']['mean']) for k,v in agg.items()])

        for k,v in agg.items():
            try:
                meanPayoffs[k].append(v['dPayoff']['mean'])
            except:
                meanPayoffs[k] = [v['dPayoff']['mean']]
        #k,v['dPayoff']['mean']) for k,v in agg.items()
    return meanPayoffs



def makePlots(descDic):
    
    pl.close("all")
    
    for M in [1,2,3,5,7,9]:
        descDic['M'] = M
        dic = showPayoffAggregates(descDic)
        
        pl.figure(1)
        pl.plot(dic ['s'][1:],np.array(dic['E']) + np.array(dic['FM']))
        pl.xlabel("s")
        pl.ylabel("diff(dPayoff E - dPayoff FM)")
        
        pl.figure(2)
        pl.plot(dic['s'][:],np.array(dic['M']))
        pl.xlabel("s")
        pl.ylabel("dPayoff M ")

        pl.figure(3)
        pl.plot(dic['s'][1:],np.array(dic['E']))
        pl.xlabel("s")
        pl.ylabel("dPayoff E ")
        
        pl.figure(4)
        pl.plot(dic['s'][1:],np.array(dic['FM']))
        pl.xlabel("s")
        pl.ylabel("dPayoff FM ")
        
        pl.figure(5)
        pl.plot(dic['s'][:],np.array(dic['U']),label=str(M))
        pl.xlabel("s")
        pl.ylabel("dPayoff U")
        
    pl.legend(loc=0)
    

def makeXY(dic):
    x = dic['iter']  
    y = dic['values']
    return x,y

def plotSeries(dic,smoothing = 10,logx=False):
    
    x,y = makeXY(dic)
    
    ySconv = np.convolve(y,np.zeros([smoothing])+1./smoothing)[:-smoothing+1]

    if logx:
        pl.semilogx(x,ySconv)
    else:
        pl.plot(x,ySconv)
    
    pl.xlabel("iterations")
    pl.ylabel("value")
   
def plotAllSeries(filename,logx=False):
    pl.close("all")
    
    agg = aggregates(filename)
    
    pl.figure(1)
    plotSeries(agg['E']['dPayoff']['tseries'],logx=logx)
    plotSeries(agg['FM']['dPayoff']['tseries'],logx=logx)
    plotSeries(agg['M']['dPayoff']['tseries'],logx=logx)
    plotSeries(agg['U']['dPayoff']['tseries'],logx=logx)
    
    pl.figure(2)
    plotSeries(agg['E']['mDistance']['tseries'],logx=logx)
    plotSeries(agg['FM']['mDistance']['tseries'],logx=logx)
    plotSeries(agg['M']['mDistance']['tseries'],logx=logx)
    

def plotPhaseTransition_d05(percentile=25,plot=False):
    
    descDic = {'M': 5,'h':100, 'l':100, 'cl': 0.5,  'il': 1.0, 'iter': 200, 'm': 0.0, 'ns': 4, 'q': 0.0,'d':0.5}
    resultDir = "/Users/maithoma/work/compute/pgames_d05_transition/results/"
    #print listRootFilenames()
    
    rt_fnames = selectRootFilenames(descDic)['list_rt']
    rt_variables = selectRootFilenames(descDic)['var_dic']
    
    S = []
    C = []
    s = []
    cMedian = []
    cDown = []
    cUp = []
    cCountUp = []
    cCountDown = []
    cCountMiddle = []
    
    for r,rt in enumerate(rt_fnames):
        i=0
        c = []
        s.append(rt_variables['s'][r])
        while True:
            try:
                filename = rt + "_%s.csv"%i
                coop = parseSummary(filename)['coop_level']
                print filename,coop
                c = np.append(c,coop)
                S.append(rt_variables['s'][r])
                C.append(coop)
                i+=1
            except IOError:
                break
        cMedian.append(np.median(c))
        cDown.append(np.percentile(c,percentile))
        cUp.append(np.percentile(c,100 - percentile))
        cCountUp.append(len(c[c>0.8])/float(len(c)))
        cCountDown.append(len(c[c<0.2])/float(len(c)))
        cCountMiddle.append(len(c[(c>=0.2)*(c<=0.8)])/float(len(c)))
        
    dic = {'s': s, 'cMedian': cMedian,'cUp' : cUp,'cDown' : cDown,'C' :C, 'S':S, 'cCountDown' :cCountDown, 'cCountUp' :cCountUp,'cCountMiddle' :cCountMiddle}
    
    if plot:
        pl.close("all")
        pl.figure(1)
        
        pl.plot(dic['s'],dic['cCountDown'],'r-',lw=1)
        pl.plot(dic['s'],dic['cCountUp'],'g-',lw=1)
        #pl.plot(dic['s'],dic['cCountMiddle'],'b-')
        pl.xlabel("Property Violation s")
        #pl.ylabel("Probability that cooperation wins (green) or disappears (red), \n or intermediary state (blue)")
        pl.ylim(-0.05,1.05)
        pl.xlim(xmax=0.05)
        
        pl.plot(dic['s'],dic['cMedian'],'k-.',lw=2)
        pl.fill_between(dic['s'],dic['cDown'],dic['cUp'],color='k',alpha=0.2)
        #pl.plot(dic['s'],dic['cUP'],'k-.',lw=2)
        #pl.plot(dic['s'],dic['cDown'],'k-.',lw=2)
        pl.plot(S,C,'ko')
        pl.xlabel("Property Violation s")
        pl.ylabel("Median Cooperation Level")
        

        

    return dic

