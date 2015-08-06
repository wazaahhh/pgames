from parseFiles import *



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
        except:
            print rt
            #print dDic
            continue
        
    return {'M' : M , 'd' : d , 's' :s , 'coopLevel' : coopLevel, 'variables' : rt_variables}


def meanDeltaPayoff(filename):
    
    print filename
    dic = {}
    
    parsed = parseAllMoves(filename)
    
    '''Strategy updates'''
    dpf = parsed['U']['dPayoff']
    dic['U'] = {'mean' : np.mean(dpf), 'std' : np.std(dpf),'min' : np.min(dpf), 'max' :np.max(dpf)}

    try:
        '''Mobility'''
        index = np.array(parsed['M']['moveType']) == 'M'
        i2 = np.array(parsed['M']['dPayoff']) > 0
        dpf = np.array(parsed['M']['dPayoff'])[index*i2]
        dic['M'] = {'mean' : np.mean(dpf), 'std' : np.std(dpf),'min' : np.min(dpf), 'max' :np.max(dpf)}
    except:
        dic['M'] = {'mean' : 0, 'std' :0,'min' : 0, 'max' :0}

    try:
        '''Forced Mobility'''
        index = np.array(parsed['M']['moveType']) == 'FM'
        dpf = np.array(parsed['M']['dPayoff'])[index]
        dic['FM'] = {'mean' : np.mean(dpf), 'std' : np.std(dpf),'min' : np.min(dpf), 'max' :np.max(dpf)}

    
        '''Property Violation'''
        index = np.array(parsed['M']['moveType']) == 'E'
        dpf = np.array(parsed['M']['dPayoff'])[index*i2]
        dic['E'] = {'mean' : np.mean(dpf), 'std' : np.std(dpf),'min' : np.min(dpf), 'max' :np.max(dpf)}
    except:
        dic['FM'] = {'mean' : 0, 'std' :0,'min' : 0, 'max' :0}
        dic['E'] = {'mean' : 0, 'std' :0,'min' : 0, 'max' :0}
    
    return dic
