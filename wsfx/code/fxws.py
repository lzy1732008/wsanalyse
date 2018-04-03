import re
import jieba.analyse as pos
import math
import numpy
import os
import datetime
from util.wsfun import getFTList
from util.wsfun import getRDSS
from util.wsfun import getZKDL
from code.buildword2vector import load_models
from util.excelop import createx


# 首先对文书进行停用词过滤
# 得到文书引用法条内容分组
# 对于每个法条内容遍历文书RDSS+ZKDL
# 计算方式：1、对法条内容进行切割“。；”得到sp
# 2、对每个法条sp进行提取关键词，保留权重，关键词个数为math.ceil（len/5）
# 3、对于每个sp得到的关键词词典，遍历文书内容，
# 4、文书内容关键词个数为math.ceil(len/5)
# 5、寻找法条sp中相似度最高的相似值*权重

def cutcontent(content):
    return list(filter(lambda x: x.strip() != '', re.split('；|。', content)))


def matchobject(wspath):
    return getRDSS(wspath) + getZKDL(wspath)


def getkeys(content):
    return pos.extract_tags(content, topK=math.ceil(len(content) / 5), withWeight=True)

#将人名、地名等过滤掉
#建立停用词库
def filterkeys(content,kw):
    pass


def getnormalizeweigth(kw,flag):
    dict = getkeys(kw)
    keys = []
    weights = []
    sum = 0
    for k, w in dict:
        sum += w
        keys.append(k)
    for k, w in dict:
        w = w / sum
        weights.append(w)
    if flag:
        return keys,weights
    return keys


def traversews(wspath, modelpath):
    #加入data
    outputdata = []


    model = load_models(modelpath)
    ftmcls, ftnrls = getFTList(wspath)
    print('wsft..', ftmcls)
    wsStrls = cutcontent(matchobject(wspath))
    wsStrkeys = []
    # 预先将文书所有句子的关键词提取好
    for wsStr in wsStrls:
        wsStrkeys.append(getnormalizeweigth(wsStr,False)) #h获取文书关键词，[[]]
    print('set ws keys length....', len(wsStrkeys))

    # 遍历法条
    for ftnr in ftnrls:
        #加入法条data
        ftdata = []

        print('ftnr', ftnr)
        ftnrArra = cutcontent(ftnr)
        print('ftnrArra lenght..', len(ftnrArra))

        #优化，将nr对应的keys先算好，存进dict中
        nrkeysdict = {}
        for nr in ftnrArra:
            keys, weights = getnormalizeweigth(nr, True)
            nrkeysdict[nr] = [keys,weights]



        #update  对于每个句子都把法条sp遍历比较一遍
        for i in range(len(wsStrkeys)):
            wsStrkey = wsStrkeys[i]
            wsStr = wsStrls[i]
            smaxsum = -100

            print('wsStr', wsStr)
            for nr in ftnrArra:
                sum = 0  # 法条sp级别的和
                # print('nr in ftnrArra', nr)
                # keys, weights = getnormalizeweigth(nr, True)
                #优化
                nrdict = nrkeysdict[nr]
                keys = nrdict[0]
                weights = nrdict[1]

                for j in range(len(keys)):
                    maxsim = -1  # 对于当前关键词到文书关键词进行匹配
                    ftk = keys[j]
                    ftw = weights[j]
                    for wsk in wsStrkey:
                        try:
                            sim = model.n_similarity(ftk, wsk)
                            # print(ftk,wsk,sim,ftw)
                        except:
                            sim = -1
                        if sim > maxsim:
                            maxsim = sim
                        else:
                            pass
                    sum += maxsim * ftw
                # print('ft nr array:', nr)
                # print('ft nr keys:',keys)
                # print('sum', sum)

                if sum > smaxsum:  #针对该句子，是否目前法条sp中最大的sum
                    smaxsum = sum

            # if smaxsum < 0.25:
            #    print('smaxsum',smaxsum)

            ftdata.append(smaxsum)
        outputdata.append(ftdata)
    #反转
    outputArra = numpy.array(outputdata).T
    wspathsp= wspath.split('/')
    wsname = wspathsp[len(wspathsp)-1]
    createx(wsname,wsStrls,ftmcls,outputArra)








        # for nr in ftnrArra:
        #     # output test
        #     print('ftnr', nr)
        #     keys,weights = getnormalizeweigth(nr, True)
        #     # 对于法条sp遍历文书
        #     for i in range(len(wsStrkeys)):
        #         wsStrkey = wsStrkeys[i]
        #         wsStr = wsStrls[i]
        #         sum = 0  # 句子级别的和
        #         print('wsStr', wsStr)
        #
        #         for j in range(len(keys)):
        #             maxsim = -1  # 对于当前关键词到文书关键词进行匹配
        #             ftk = keys[j]
        #             ftw = weights[j]
        #             for wsk in wsStrkey:
        #                 try:
        #                     sim = model.n_similarity(ftk, wsk)
        #                 except:
        #                     sim = -1
        #                 if sim > maxsim:
        #                     maxsim = sim
        #                 else:
        #                     pass
        #             sum += maxsim * ftw
        #         if sum > 0.1:
        #            print('sum', sum)

def wsfxMain(wsdictpath,word2vecmodelpath):
    starttime = datetime.datetime.now()
    dir = os.listdir(wsdictpath)
    for i in range(500):
        wsname = dir[i]
        wspath = wsdictpath +'/'+wsname
        traversews(wspath,word2vecmodelpath)
    endtime = datetime.datetime.now()
    print((endtime-starttime).seconds)


wsdictpath = '/users/wenny/nju/task/法条文书分析/2014filled/2014'
word2vecmodelpath = '../data/2014model.model'
wsfxMain(wsdictpath,word2vecmodelpath)
# traversews('../data/testws/3562.xml', '../data/2014model.model')
