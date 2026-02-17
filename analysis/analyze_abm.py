from parseFiles import *
import pylab as pl
import numpy as np
import scipy.stats as S

global coldic
coldic = {'E' :'b', 'FM' : 'c' , 'M':'g', 'U' : 'r'}

fig_width_pt = 420.0  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0 / 72.27  # Convert pt to inch
golden_mean = (np.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
fig_width = fig_width_pt * inches_per_pt  # width in inches
fig_height = fig_width  # *golden_mean      # height in inches
fig_size = [fig_width, fig_height]


params = {'backend': 'ps',
          'axes.labelsize': 25,
          'text.fontsize': 32,
          'legend.fontsize': 12,
          'xtick.labelsize': 20,
          'ytick.labelsize': 20,
          'text.usetex': False,
          'figure.figsize': fig_size}
pl.rcParams.update(params)

resultDir = "/Users/maithoma/work/compute/pgames_d05_transition/results/"

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
            coopLevel.append(parseSummary(filename)['coop_level'][-1])
            finalIter.append(parseSummary(filename)['iter'][-1])
        except:
            print rt
            continue

    return {'M' : M , 'd' : d , 's' :s , 'coopLevel' : coopLevel, 'finalIter' :  finalIter, 'variables' : rt_variables}


def aggregates(filename,display=False):

    outdic = {}
    outdic['desc'] = parseFilename(filename[:re.search("_s_.*?(_)",filename).end()-1])['descDic']
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

def plotSeries(dic,label,smoothing = 10,logx=False):

    x,y = makeXY(dic)
    ySconv = np.convolve(y,np.zeros([smoothing])+1./smoothing)[:-smoothing+1]



    if logx:
        pl.semilogx(x,ySconv,label=label,alpha=0.6)
    else:
        pl.plot(x,ySconv,label=label,alpha=0.6)

    pl.xlabel("iterations")
    pl.ylabel("value")

def plotAllSeries(filename,logx=False):
    pl.close("all")

    agg = aggregates(filename)

    pl.figure(1,(18,8))
    pl.subplot(121)
    pl.title("Delta Payoff")
    plotSeries(agg['E']['dPayoff']['tseries'],label="property violation",logx=logx)
    plotSeries(agg['FM']['dPayoff']['tseries'],label="force move",logx=logx)
    plotSeries(agg['M']['dPayoff']['tseries'],label="migration",logx=logx)
    plotSeries(agg['U']['dPayoff']['tseries'],label="strategy update",logx=logx)
    pl.ylim(-4,5)
    pl.legend(loc=0)

    pl.subplot(122)
    pl.title("Migration Distance")
    plotSeries(agg['E']['mDistance']['tseries'],logx=logx,label="property violation")
    plotSeries(agg['FM']['mDistance']['tseries'],logx=logx,label="force move")
    plotSeries(agg['M']['mDistance']['tseries'],logx=logx,label="migration")
    pl.ylim(0,6)
    pl.legend(loc=0)
    pl.savefig("Figures/tseries_%s.eps"%filename[:-4])


def PhaseTransitionMd_all():
    descDic = {'l':100,'h':100,'cl':0.500,'ns':4,'il':1.000,'q':0.000,'m':0.000}

    rt_fnames = np.array(selectRootFilenames(descDic)['list_rt'])
    rt_var = selectRootFilenames(descDic)['var_dic']

    c = np.logical_or(np.array(rt_var['M']) != 1, np.array(rt_var['iter']) > 1000) #* (np.array(rt_var['iter']) > 0)

    m = np.array(rt_var['M'])[c]
    s = np.array(rt_var['s'])[c]
    d = np.array(rt_var['d'])[c]

    C = []
    S = []
    M = []
    D = []

    for r,rt in enumerate(rt_fnames[c]):
        i=0
        while True:
            try:
                filename = rt + "_%s.csv"%i
                #print filename
                coop = parseSummary(filename)['coop_level'][-1]
                M = np.append(M,m[r])
                S = np.append(S,s[r])
                D = np.append(D,d[r])
                C = np.append(C,coop)
                i+=1
            except IOError:
                break


    dic = {'M':M,'S':S,'C':C,'D':D}

    return dic

def PhaseTransitionMd_d():


    print resultDir

    descDic = {'l':100,'h':100,'d':0.500,'cl':0.500,'ns':4,'il':1.000,'q':0.000,'m':0.000}

    rt_fnames = np.array(selectRootFilenames(descDic)['list_rt'])
    rt_var = selectRootFilenames(descDic)['var_dic']

    c = np.logical_or(np.array(rt_var['M']) != 1, np.array(rt_var['iter']) > 1000) #* (np.array(rt_var['iter']) > 0)
    #c2 =  (np.array(rt_var['iter']) >= 1000)
    #c = c*c2

    m = np.array(rt_var['M'])[c]
    s = np.array(rt_var['s'])[c]

    C = []
    S = []
    M = []


    for r,rt in enumerate(rt_fnames[c]):
        i=0
        while True:
            try:
                filename = rt + "_%s.csv"%i
                #print filename
                coop = parseSummary(filename)['coop_level'][-1]
                M = np.append(M,m[r])
                S = np.append(S,s[r])
                C = np.append(C,coop)
                i+=1
            #except IOError:
            #    break

            except:
                print filename
                break


    dic = {'M':M,'S':S,'C':C}

    return dic

def plotPhaseTransitionMd(dic):
    M = dic['M']
    S = dic['S']
    C = dic['C']

    pl.close("all")

    colors = ['b','g','r','c','m','y','c']

    pl.figure(1,(11,9))

    for i,m in enumerate(np.unique(M)):
        print m
        if m == 4:#or m == 3:
            continue
        index = np.argwhere(M == m)

        B = binning(S[index],C[index],50,confinter=0.01)
        pl.fill_between(B['bins'],B['percUp'],B['percDown'],alpha=0.05,color = colors[i])
        pl.plot(B['bins'],B['mean'],'x-',label="M = %s"%m,color = colors[i],lw=1)
        pl.plot(B['bins'],B['percUp'],'-.',color = colors[i])
        pl.plot(B['bins'],B['percDown'],'-.',color = colors[i])
        pl.plot(S[index],C[index],"o",color = colors[i])

    pl.xlabel("Property violation s")
    pl.ylabel("Cooperation level c")
    pl.legend(loc=0)
    pl.xlim(xmax = 0.1)
    return B

def plotPhaseTransition_d05(descDic,percentile=25,plot=False):

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
                #print filename
                coop = parseSummary(filename)['coop_level'][-1]
                #print filename,coop
                c = np.append(c,coop)
                S.append(rt_variables['s'][r])
                C.append(coop)
                i+=1
            except IOError:
                break
        print rt,c
        cMedian.append(np.mean(c))
        cDown.append(np.percentile(c,percentile))
        cUp.append(np.percentile(c,100 - percentile))
        cCountUp.append(len(c[c>0.8])/float(len(c)))
        cCountDown.append(len(c[c<0.2])/float(len(c)))
        cCountMiddle.append(len(c[(c>=0.2)*(c<=0.8)])/float(len(c)))

    dic = {'s': s, 'cMedian': cMedian,'cUp' : cUp,'cDown' : cDown,'C' :C, 'S':S, 'cCountDown' :cCountDown, 'cCountUp' :cCountUp,'cCountMiddle' :cCountMiddle}

    if plot:
        pl.close("all")
        pl.figure(1)

        #pl.plot(dic['s'],dic['cCountDown'],'r-+',lw=1)
        #pl.plot(dic['s'],dic['cCountUp'],'g-x',lw=1)
        #pl.plot(dic['s'],dic['cCountMiddle'],'b-')
        pl.xlabel("Property Violation s")
        #pl.ylabel("Probability that cooperation wins (green) or disappears (red), \n or intermediary state (blue)")
        pl.ylim(-0.05,1.05)
        #pl.xlim(xmax=0.05)

        pl.plot(dic['s'],dic['cMedian'],'k-.',lw=2)
        pl.fill_between(dic['s'],dic['cDown'],dic['cUp'],color='k',alpha=0.2)
        #pl.plot(dic['s'],dic['cUP'],'k-.',lw=2)
        #pl.plot(dic['s'],dic['cDown'],'k-.',lw=2)
        pl.plot(S,C,'ko')
        pl.xlabel("Property Violation s")
        pl.ylabel("Median Cooperation Level")




    return dic


def expectedDPayoffs(filename,plotRankLag=True):

    dic = parseAllMoves(filename)
    summary = parseSummary(filename)
    l = summary['iter'][-1]
    bins = np.arange(0,l,2000)
    nBinB = 200
    binB = np.linspace(1,l,nBinB)
    halfLimit = 50
    print "half limit: ", float(binB[halfLimit])/l
    #indexCoopMax = np.argmax(summary['coop_level'])
    #iterCoopMax = summary['iter'][indexCoopMax]
    #halfLimit = np.argwhere(binB > iterCoopMax)[0][0]


    confinter = 25

    outdic = {}

    pl.close("all")
    fig = pl.figure(1)
    fig1 = fig.add_subplot(111)
    pl.xlabel("iterations")
    pl.ylabel("dPayoff(t) x Rate(t) (log10 scale)")
    pl.ylim(0,3)

    fig2 = fig1.twinx()
    iter = np.array(summary['iter'])
    coop = np.array(summary['coop_level'])
    c = (iter > 0)*(coop > 0)
    fig2.plot(np.log10(iter[c]),coop[c],'k-',lw=2)

    yLimit = np.linspace(0,1,10)
    #print halfLimit/nBinB*float(l),halfLimit,nBinB,l
    xLimit = np.zeros_like(yLimit)+(float(halfLimit)/float(nBinB)*float(l))
    #print xLimit,yLimit
    fig2.plot(np.log10(xLimit),yLimit,'y-',lw=2)

    pl.ylabel("Cooperation Level (black line)")
    pl.ylim(0,1)
    #print dic.keys()

    for key,value in dic.items():

        try:

            #print value.keys()
            H = np.histogram(value['iter'], bins,weights=value['dPayoff'],density=False)

            if key == "FM":
                continue
                #print "blah"
                #print - H[0]
                #H[0][:] = -H[0]

            #print key
            Blog10 = binning(H[1][:-1],H[0],binB,confinter=confinter,log_10=True)
            #pl.loglog(H[1][:-1],H[0],label=key,alpha=0.7)
            c = (Blog10['bins'] > 0)*(Blog10['median'] > 0)*(Blog10['percDown'] > 0)*(Blog10['percUp'] > 0)
            fig1.plot(Blog10['bins'],Blog10['median'],'.-',color=coldic[key],label=key)
            fig1.fill_between(Blog10['bins'][c],Blog10['percUp'][c],Blog10['percDown'][c],color=coldic[key],alpha=0.6)
            pl.xlim(Blog10['bins'][0],Blog10['bins'][-1])
            B = binning(H[1][:-1],H[0],binB,confinter=confinter,log_10=False)

        except:
            continue

        mean = np.mean(value['dPayoff'])
        count = len(value['dPayoff'])
        outdic[key] = {'mean' : mean, 'count': count,'Blog10' : Blog10, 'B' : B,'H' : H}

    pl.legend(loc=0)
    numerator = 0
    denominator = 0

    for key in outdic.keys():
        #print key, outdic[key]
        numerator += outdic[key]['count']*outdic[key]['mean']
        denominator += outdic[key]['count']

    if plotRankLag:
        listKeys = ['E','U','M']
        pl.figure(3,(13,7))
        for k1,kx1 in enumerate(listKeys):
            for k2,kx2 in enumerate(listKeys):

                for half in ['firstHalf','secondHalf']:
                    if half == 'firstHalf':
                        l,rho = crossLagCorr(outdic[kx1]['B'][1][:halfLimit],outdic[kx2]['B'][1][:halfLimit])
                        pl.subplot(121)
                    else:
                        l,rho = crossLagCorr(outdic[kx1]['B'][1][halfLimit:],outdic[kx2]['B'][1][halfLimit:])
                        pl.subplot(122)

                    if k2 > k1:
                        pl.plot(l,rho,label="%s -> %s"%(kx1,kx2))
                    #elif k2==k1:
                    #    pl.plot(l,rho,'--',label="%s -> %s"%(kx1,kx2))
                    else:
                        continue


        y = np.linspace(0,1,10)
        pl.subplot(121)
        pl.plot(np.zeros_like(y),y,'k-')
        pl.xlabel("lag [bins]")
        pl.ylabel("Spearman rho")
        pl.legend(loc=0)
        pl.ylim(0,1)

        pl.subplot(122)
        pl.plot(np.zeros_like(y),y,'k-')
        pl.xlabel("lag [bins]")
        pl.ylabel("Spearman rho")
        pl.legend(loc=0)
        pl.ylim(0,1)
    return outdic

def migrationDistance(filename):

    dic = parseAllMoves(filename)
    summary = parseSummary(filename)
    l = summary['iter'][-1]
    bins = np.arange(0,l,2000)
    nBinB = 200
    binB = np.linspace(1,l,nBinB)

    confinter = 25

    pl.close("all")

    pl.figure(2)
    fig = pl.figure(2)
    fig1 = fig.add_subplot(111)
    pl.xlabel("iterations (log10 scale)")
    pl.ylabel("mDistance(t) x Rate(t) (log10 scale)")
    pl.ylim(0,4)

    fig2 = fig1.twinx()
    iter = np.array(summary['iter'])
    coop = np.array(summary['coop_level'])
    c = (iter > 0)*(coop > 0)
    fig2.plot(np.log10(iter[c]),coop[c],'k-',lw=2)
    pl.ylabel("Cooperation Level (black line)")
    pl.ylim(0,1)

    for key,value in dic.items():
        try:
            print key,len(value['mDistance'])


            H = np.histogram(value['iter'], bins,weights=value['mDistance'],density=False)

            #if key == "FM":
            #    continue

            Blog10 = binning(H[1][:-1],H[0],binB,confinter=confinter,log_10=True)

            c = (Blog10['bins'] > 0)*(Blog10['median'] > 0)*(Blog10['percDown'] > 0)*(Blog10['percUp'] > 0)
            fig1.plot(Blog10['bins'],Blog10['median'],'.-',color=coldic[key],label=key)
            fig1.fill_between(Blog10['bins'][c],Blog10['percUp'][c],Blog10['percDown'][c],color=coldic[key],alpha=0.6)
            pl.xlim(Blog10['bins'][0],Blog10['bins'][-1])
            B = binning(H[1][:-1],H[0],binB,confinter=confinter,log_10=False)

        except:
            continue

    pl.legend()
    return B,H


def crossLagCorr(x,y,lagspan=35):

    rho = []
    L = range(-lagspan,lagspan)

    for l in L:
        if l==0:
            rho.append(S.spearmanr(x,y)[0])
        elif l < 0:
             rho.append(S.spearmanr(x[-l:],y[:l])[0])
        else:
            rho.append(S.spearmanr(x[:-l],y[l:])[0])

    return L,rho


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
