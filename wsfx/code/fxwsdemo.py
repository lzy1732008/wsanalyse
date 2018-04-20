import re
import jieba.analyse as pos
import math
import numpy
import os
import datetime
from wsfx.util.wsfun import getFTList
from wsfx.util.wsfun import getRDSS
from wsfx.util.wsfun import getZKDL
from wsfx.util.wsfun import getQWChildContent
from wsfx.code.buildword2vector import load_models
from wsfx.util.excelop import createx
from wsfx.util.fileop import writejson
from wsfx.util.contentop import cutcontent
from wsfx.util.calculate import calculatews
from wsfx.util.fileop import getlines
import random
import numpy


# 首先对文书进行停用词过滤
# 得到文书引用法条内容分组
# 对于每个法条内容遍历文书RDSS+ZKDL
# 计算方式：1、对法条内容进行切割“。；”得到sp
# 2、对每个法条sp进行提取关键词，保留权重，关键词个数为math.ceil（len/5）
# 3、对于每个sp得到的关键词词典，遍历文书内容，
# 4、文书内容关键词个数为math.ceil(len/5)
# 5、寻找法条sp中相似度最高的相似值*权重


# 获取事实内容
def getSSMatchObject(wspath):
    return getRDSS(wspath) + getZKDL(wspath)


# 获取结论内容
def getJLMatchObject(wspath):
    return getQWChildContent(wspath, 'CPFXGC') + getQWChildContent(wspath, 'PJJG')


def getkeys(content):
    return pos.extract_tags(content, topK=math.ceil(len(content) / 5), withWeight=True)


# 将人名、地名等过滤掉
# 建立停用词库
def filterkeys(content, kw):
    pass


def getnormalizeweigth(kw, flag):
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
        return keys, weights
    return keys


# wsStrkey：一个文书句子的关键词列表
# ftnrArra：文书句子列表
# nrkeysdict：一个法条再进行切分后，每个子句子对应的关键词及其权重的词典，形式为：{'ftnrsp',[keys, weights]}
# wsStr:一个文书句子
# model：word2vec模型
# 返回该文书句子与该法条的匹配度
def distance(wsStrkey, ftnrArra, nrkeysdict, wsStr, model):
    smaxsum = -100
    # print('Str', wsStr)
    for nr in ftnrArra:
        sum = 0  # 法条sp级别的和
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

        if sum > smaxsum:  # 针对该句子，是否目前法条sp中最大的sum
            smaxsum = sum
    return smaxsum


# 将该文书事实和结论与法条进行映射
def traversews(wspath, model):
    # 加入data
    # outputdata_dict = {}
    outputdata_ss = []
    outputdata_jl = []

    ftmcls, ftnrls = getFTList(wspath)
    print('wsft..', ftmcls)
    wsStrls = cutcontent(getSSMatchObject(wspath))
    wsStrkeys = []
    # 预先将文书所有句子的关键词提取好
    for wsStr in wsStrls:
        wsStrkeys.append(getnormalizeweigth(wsStr, False))  # h获取文书关键词，[[]]
    print('set ws sp length....', len(wsStrkeys))

    # 预先将结论所有句子的关键词提取好
    jlStrkeys = []
    jlStrls = cutcontent(getJLMatchObject(wspath))
    for jlStr in jlStrls:
        jlStrkeys.append(getnormalizeweigth(jlStr, False))
    print('set jl sp length....', len(jlStrkeys))

    # 遍历法条
    for i in range(len(ftnrls)):
        # 加入法条data
        ftdata_ss = []
        ftdata_jl = []

        ftnr = ftnrls[i]
        ftmc = ftmcls[i]
        print('ftnr', ftnr)
        ftnrArra = cutcontent(ftnr)
        print('ftnrArra lenght..', len(ftnrArra))

        # 优化，将nr对应的keys先算好，存进dict中
        nrkeysdict = {}
        for nr in ftnrArra:
            keys, weights = getnormalizeweigth(nr, True)
            nrkeysdict[nr] = [keys, weights]

        #   对于每个事实句子都把法条sp遍历比较一遍
        for i in range(len(wsStrkeys)):
            wsStrkey = wsStrkeys[i]
            wsStr = wsStrls[i]
            smaxsum = distance(wsStrkey, ftnrArra, nrkeysdict, wsStr, model)
            if smaxsum > 0.25:
               ftdata_ss.append(1)
            else:
                ftdata_ss.append(0)
            # print('ws nr',wsStr)
            # print('ws keys',wsStrkey)
            # print('ws ft max distance',smaxsum)

        # 对于每个结论句子都把法条sp遍历比较一遍
        for i in range(len(jlStrkeys)):
            jlStrkey = jlStrkeys[i]
            jlStr = jlStrls[i]
            smaxsum = distance(jlStrkey, ftnrArra, nrkeysdict, jlStr, model)
            if smaxsum > 0.45:
               ftdata_jl.append(1)  # error1
            else:
                ftdata_jl.append(0)
        # outputdata_dict[ftmc] = [ftdata_ss,ftdata_jl]
        outputdata_ss.append(ftdata_ss)
        outputdata_jl.append(ftdata_jl)
    # 输出到法条与事实的映射list，以及法条到结论映射list
    return outputdata_ss, outputdata_jl

    # 反转输出到excel中
    # outputArra_ss = numpy.array(outputdata_ss).T
    # outputArra_jl = numpy.array(outputdata_jl).T
    # wspathsp = wspath.split('/')
    # wsname = wspathsp[len(wspathsp) - 1]
    # createx(wsname, jlStrls, ftnrls, outputArra_jl,'../data/testwsoutput_ft2jl_2')
    # createx(wsname, wsStrls, ftnrls, outputArra_ss, '../data/testwsoutput_ss2ft_2')


# 输入文书路径和word2vec模型
# 输出事实到法条的映射关系以及法条到结论的映射关系

def wsfx(wsdictpath, word2vecmodelpath, datapath):
    # starttime = datetime.datetime.now()
    # dir = os.listdir(wsdictpath)#随机获取文书所用

    word2vecmodel = load_models(word2vecmodelpath)
    # 生成500个随机数： #随机获取文书所用
    # resultList = random.sample(range(0, 40000), 20);
    # for i in resultList:
    #     wsname = dir[i]
    #     wspath = wsdictpath + '/' + wsname
    #     traversews(wspath, word2vecmodel)
    # endtime = datetime.datetime.now()
    # print((endtime - starttime).seconds)

    outputdata_ss, outputdata_jl = traversews(wsdictpath, word2vecmodel)
    # 对数据进行处理，并计算准确率和召回率
    print('utputdata_jl',outputdata_jl)
    output_ss = numpy.reshape(outputdata_ss, (1, len(outputdata_ss) * len(outputdata_ss[0])))[0]
    output_jl = numpy.reshape(outputdata_jl, (1, len(outputdata_jl) * len(outputdata_jl[0])))[0]

    truedata = []
    datapath = datapath + '/' + wsdictpath.split('/')[-1].split('.xml')[0] + '.txt'
    lines = getlines(datapath)
    for line in lines:
        truedata.append(int(line.split('!@#')[-1]))
    print('truedata', truedata)
    print('outputjl', output_jl)
    return calculatews(output_jl, truedata, flag=2)





# wsdictpath = '../data/testws'
# datapath = '../data/testdata_jl'

# wsdictpath = '/users/wenny/nju/task/法条文书分析/2014filled/2014'
# # wsdictpath = '../data/testws'

def wsfxMain(wspath):
    word2vecmodelpath = '../data/2014model.model'
    # wsfxMain(wsdictpath, word2vecmodelpath, datapath)
    word2vecmodel = load_models(word2vecmodelpath)
    print(traversews(wspath, word2vecmodel))

wsfxMain('../data/testws/90898.xml')

