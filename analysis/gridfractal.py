import numpy as np
import pylab as pl
from scipy import stats as S
import boto
import json

from s3 import pullTogether
#s3 = boto.connect_s3()
#global bucket
#bucket = s3.get_bucket("pgame")
#bucketviz = s3.get_bucket("pgameviz")


def allsites_within_range(player_l,player_h,l,h,migration_range,exclude_focal_site=True):
    k = 0

    sites_index = []

    for i in range(player_h - migration_range , player_h + migration_range + 1):
        for j in range(player_l - migration_range , player_l + migration_range + 1):
            l_index = (i + l)%l;
            h_index = (j + h)%h;

            if exclude_focal_site and l_index == player_l and h_index == player_h:
				continue

            #print l_index,h_index,l_index + h_index * l

            sites_index.append(l_index + h_index * l)
			#migration_array_l[k] = l_index;
			#migration_array_h[k] = h_index;
            k += 1

    return sites_index


def localDensity(listGrid,player_l,player_h,l=50,h=50,M=5):

    sites_index = allsites_within_range(player_l,player_h,l,h,M,exclude_focal_site=False)

    localRho = 0
    localCoopRho = 0
    localDefectRho= 0

    rho = {}

    for i in [-1,0,1]:
        states = np.array([listGrid[s] for s in sites_index])
        c = states == i
        rho[i] = len(states[c])

    '''
    for site,state in enumerate(listGrid):
        if site in sites_index:
            if state != -1: localRho += 1
            if state == 0: localDefectRho += 1
            if state == 1: localCoopRho += 1
            #print state,
    #print
    rho = np.array([localRho,localCoopRho,localDefectRho])/float(len(sites_index))
    #print player_l,player_h,rho
    '''
    return {'localRho' : (rho[-1]) / float(len(sites_index)),
            'localCoopRho' : rho[1] / float(len(sites_index)),
            'localDefectRho' : rho[0] / float(len(sites_index))}

def globalDensity(listGrid,l=50,h=50,M=5):

    listGrid = np.array(listGrid)

    O = []
    C = []
    D = []

    for site in range(len(listGrid)):
        player_l = site % h
        player_h = site / h
        dic = localDensity(listGrid,player_l,player_h,l=50,h=50,M=5)

        O.append(dic['localRho'])
        C.append(dic['localCoopRho'])
        D.append(dic['localDefectRho'])

    return {'O':O,'C':C,'D':D}


def timeGlobalDensity(Jraw):

    O = []
    C = []
    D = []
    I = []

    dic = {'I' : [],'O': {},'C' : {},'D' : {}}

    grids = Jraw['grids'].split("\n")
    iterations = np.unique(map(int,np.logspace(0,np.log10(len(grids)-2),10)))
    #print iterations

    for g in iterations:
        #print g
        iter = grids[g].split(":")[0]
        grid = grids[g].split(":")[1]
        listGrid = map(int,grid[1:-2].split(","))
        metrics= globalDensity(listGrid,l=50,h=50,M=5)

        dic['I'].append(iter)

        for metric in ['O','C','D']:
            for function in [np.mean,np.std,S.skew]:
                try:
                    dic[metric][str(function)[10:-16]].append(function(metrics[metric]))
                except:
                    dic[metric][str(function)[10:-16]] = [function(metrics[metric])]

    return dic

def roughBootstrap(function):

    rootDir = '/Users/maithoma/work/compute/viz_transition/'

    pl.close("all")
    pl.figure(1,(21,7))

    w = [0,2,5,1,6,8,9,10,11,12,13,14,16,17,18,19,21,22,23]
    l = [3,4,7,15,20,24]

    colors = ['k','g','r']

    for i in w:
        print i
        fname = "iter_200_l_50_h_50_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0400_%s.csv"%i
        Jraw = pullTogether(rootDir,fname,compress=False)
        dic = timeGlobalDensity(Jraw)

        for j,jx in enumerate(['O','C','D']):
            pl.subplot(130 + j)
            pl.semilogx(dic['I'],dic[jx][function],"--",color=colors[j])

    for i in l:
        print i
        fname = "iter_200_l_50_h_50_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0400_%s.csv"%i
        Jraw = pullTogether(rootDir,fname,compress=False)
        dic = timeGlobalDensity(Jraw)
        for j,jx in enumerate(['O','C','D']):
            pl.subplot(130 + j)
            pl.semilogx(dic['I'],dic[jx][function],"-",color=colors[j])

#if __name__ == '__main__':

#    keyCoopWins =  	"iter_200_l_50_h_50_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0400_4_e10a8.json"
#    keyCoopLoss = "iter_200_l_50_h_50_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0400_3_69111.json"

    #key = bucketviz.get_key(keyCoopLoss)
    #J = json.loads(key.get_contents_as_string())

    #J['grids'].keys()
