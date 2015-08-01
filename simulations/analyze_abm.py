from parseFiles import *



def cooperationLevel():
    rt_fnames = listRootFilenames()
    
    M = []
    d = []
    s = []
    coopLevel = []
    meanMigration = []
    meanDeltaPayoff = []
    
    for rt in rt_fnames:
        try:
            dList = parseFilename(rt)
            description = dict(zip(*[zip(*dList)[0],zip(*dList)[2]]))
            M.append(description['M'])
            d.append(description['d'])
            s.append(description['s']),
            
            filename = makeFilename(dList)
            coopLevel.append(parseSummary(filename)['coop_level'])

            
        except:
            print rt
            print description
            continue
        
    return {'M' : M , 'd' : d , 's' :s , 'coopLevel' : coopLevel}


def meanDeltaPayoff(filename):
    
    dic = {}
    
    parsed = parseAllMoves(filename)
    
    '''Strategy updates'''
    dpf = parsed['U']['dPayoff']
    dic['U'] = {'mean' : np.mean(dpf), 'std' : np.std(dpf),'min' : np.min(dpf), 'max' :np.max(dpf)}

    '''Mobility'''
    index = np.array(parsed['M']['moveType']) == 'M'
    dpf = np.array(parsed['M']['dPayoff'])[index]
    dic['M'] = {'mean' : np.mean(dpf), 'std' : np.std(dpf),'min' : np.min(dpf), 'max' :np.max(dpf)}

    '''Forced Mobility'''
    index = np.array(parsed['M']['moveType']) == 'FM'
    dpf = np.array(parsed['M']['dPayoff'])[index]
    dic['FM'] = {'mean' : np.mean(dpf), 'std' : np.std(dpf),'min' : np.min(dpf), 'max' :np.max(dpf)}

    '''Property Violation'''
    index = np.array(parsed['M']['moveType']) == 'E'
    dpf = np.array(parsed['M']['dPayoff'])[index]
    dic['E'] = {'mean' : np.mean(dpf), 'std' : np.std(dpf),'min' : np.min(dpf), 'max' :np.max(dpf)}
    
    return dic

def prepareForXYZ(M=5):
    
    parDic = cooperationLevel()
    index = np.argwhere(np.array(parDic['M'])==M).flatten()
    
    x = np.array(parDic['d'])[index]
    y = np.array(parDic['s'])[index]
    z = np.array(parDic['coopLevel'])[index]

    print len(x),len(y),len(z)
    
    xStr = ",".join([str(i) for i in x])
    yStr = ",".join([str(i) for i in y])
    zStr = ",".join([str(i) for i in z])
    
    
    print xStr , "\n"
    print yStr , "\n"
    print zStr , "\n"