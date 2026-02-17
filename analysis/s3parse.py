from s3 import *

parse_version = "0.1"

def parseFilename(filename):
    '''Extract parameters from rootFilename'''
    fname = filename[:-18].split("_")

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


def parseSummary(dic):
    '''Parse intermediary and final states'''
    fieldNames = ['iter','completion','coop_level','cooperators','defectors','empty']
    summaryDic = {}

    for l,line in enumerate(dic['summary'].split("\n")[1:-1]):

        line = line[:-1].split(",")

        for i,value in enumerate(line):
            try:
                value = int(value)
            except ValueError:
                value = float(value)


            try:
                summaryDic[fieldNames[i]].append(value)
            except:
                summaryDic[fieldNames[i]] = [value]

    return summaryDic


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


def parseAllMoves(dic):
    '''Self documented'''

    outdic = {'M': {}, 'E': {},'FM':{},'RM':{},'RE':{},'U':{},'R':{}}

    for l,line in enumerate(dic['allmoves'].split("\n")[:-1]):
        line = line.split(",")
        #print line
        try:
            parseItems(parseLine(line),outdic[line[4]])
        except:
            print line
            continue

    return outdic

def load_parse(filename,reparse=False):

    key = bucket.get_key("parsed/%s/%s"%(parse_version,filename))
    if key and not reparse:
        print "loading from S3"
        dic = json.loads(zlib.decompress(key.get_contents_as_string()))
        return dic

    else:
        descDic = parseFilename(filename)
        dic = getJson("results/" + filename)
        moves = parseAllMoves(dic)
        summaryDic = parseSummary(dic)

        dic = {'summary': summaryDic, 'moves' : moves, 'description' : descDic}

        key = bucket.new_key("parsed/%s/%s"%(parse_version,filename))
        key.set_contents_from_string(zlib.compress(json.dumps(dic)))

        return dic


if __name__ == '__main__':

    filename = "iter_1000_l_100_h_100_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_3_m_0.000_s_0.0200_0_142a0.json.zlib"
    #dic = getJson("results/" + filename)
