import re
import jieba.analyse as pos
import jieba
import math
import numpy
import os
import jieba.posseg as pseg
import datetime
from wsfx.util.wsfun import getFTList
from wsfx.util.wsfun import getFTfromQW
from wsfx.util.wsfun import getSSMatchObject
from wsfx.util.wsfun import getJLMatchObject
from wsfx.code.buildword2vector import load_models
from wsfx.util.excelop import createx
from wsfx.util.excelop import getexceldata
from wsfx.util.fileop import getexcelwslist
from wsfx.util.contentop import cutcontent
from wsfx.util.calculate import calculatews
from wsfx.util.fileop import getlines
from wsfx.util.fileop import getlinesGBK
from wsfx.util.fileop import readkeysjson
import numpy
from wsfx.LDAmodel.predicttp import getLDAmodel
from wsfx.LDAmodel.predicttp import predict
from wsfx.util.fileop import gettyc

from wsfx.util.fileop import getftkeys

# 首先对文书进行停用词过滤
# 得到文书引用法条内容分组
# 对于每个法条内容遍历文书RDSS+ZKDL
# 计算方式：1、对法条内容进行切割“。；”得到sp
# 2、对每个法条sp进行提取关键词，保留权重，关键词个数为math.ceil（len/5）
# 3、对于每个sp得到的关键词词典，遍历文书内容，
# 4、文书内容关键词个数为math.ceil(len/5)
# 5、寻找法条sp中相似度最高的相似值*权重

stopwords = getlines('../data/stopwords.txt')
num20 = getlines('../data/num<20words.txt')
tyc = getlinesGBK('../data/同义词.txt')
def getkeys(content):
    kw = pos.extract_tags(content, topK=math.ceil(len(content) / 7) + 2, withWeight=True)
    return kw


# 将人名、地名等过滤掉
# 建立停用词库
def filterkeys(content, kw):
    pass


def getnormalizeweigth(wsStr, flag):
    dict = getkeys(wsStr)
    keys = []
    weights_init = []
    weights = []
    sum = 0

    filterkeys = []
    words = pseg.cut(wsStr)


    #过滤存数字、地名=========================
    for word, cx in words:
        if cx == 'nr' or cx == 'p' or cx == 'ns' or str(word).isdigit() == True or word in stopwords or word in num20 :
            filterkeys.append(word)


    for k, w in dict:
        if k not in filterkeys:
           sum += w
           keys.append(k)
           weights_init.append(w)
    for w in weights_init:
        weights.append(w/sum)
    # for w in weights:
    #     w = w / sum
    #     weights.append(w)
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
            sum +=  maxsim * ftw
        # print('ft nr array:', nr)
        # print('ft nr keys:',keys)
        # print('sum', sum)

        if sum > smaxsum:  # 针对该句子，是否目前法条sp中最大的sum
            smaxsum = sum
    return smaxsum
def distance2(wsStrkey, ftnrArra, nrkeysdict, wsStr, model):
    smaxsum = -100
    for nr in ftnrArra:
        sum = 0  # 法条sp级别的和
        nrdict = nrkeysdict[nr]
        keys = nrdict[0]
        l = 0
        if len(keys) > 4:
            keys = keys[:4]
            l = 4
        else:
            l = len(keys)
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
            sum +=  maxsim

        if sum > smaxsum/l:  # 针对该句子，是否目前法条sp中最大的sum
            smaxsum = sum
    return smaxsum



def mapkey(wsnr,keys,model,vocab):
    wssp = list(jieba.cut(wsnr))
    wsmap = []
    for key in keys:
        for c in wssp:
            try:
               if c.find(key) > -1 or key.find(c)> -1:
                   wsmap.append(key)
            except:
               pass
    return wsmap





def usekeys(wspath, model):
    outputdata_ss = []
    outputdata_jl = []

    ftmcls, ftnrls = getFTList(wspath)
    print('wsft..', ftmcls)
    ssStrls = cutcontent(getSSMatchObject(wspath))


    # 预先将结论所有句子的关键词提取好
    jlStrls = cutcontent(getJLMatchObject(wspath))


    # 获取关键词json文件
    keys = readkeysjson('../data/交通肇事罪.json')
    with open('../data/2014corpus.txt', 'r', encoding='utf-8') as f:
        vocab = list(f.read().split(' '))
    for ssStr in ssStrls:
        line = []
        mk = mapkey(ssStr,keys,model,vocab)
        for ft in ftnrls:
            f = 0
            for key in mk:
                if ft.find(key) > 0:
                    line.append(1)
                    f = 1
                    break
            if f == 0:
                line.append(0)
        outputdata_ss.append(line)


    # for jlStr in jlStrls:
    #     mk = mapkey(jlStr,keys,model,vocab)
    #     line = []
    #     for ft in ftnrls:
    #         f = 0
    #         for key in mk:
    #             if ft.find(key) > 0:
    #                 line.append(1)
    #                 f = 1
    #                 break
    #         if f == 0:
    #             line.append(0)
    #     outputdata_jl.append(line)
    return numpy.array(outputdata_ss).T




# 将该文书事实和结论与法条进行映射
def traversews(expath, model):
    # 加入data

    outputdata_ss = []
    outputdata_jl = []



    ftmcls, ftnrls = getFTList(expath)
    print('wsft..', ftmcls)
    # wsStrls = cutcontent(getSSMatchObject(wspath))
    # wsStrkeys = []
    # 预先将文书所有句子的关键词提取好
    # for wsStr in wsStrls:
    #     wsStrkeys.append(getnormalizeweigth(wsStr, False))  # h获取文书关键词，[[]]
    # print('set ws keys length....', len(wsStrkeys))

    # 预先将结论所有句子的关键词提取好
    jlStrkeys = []
    jlStrls = cutcontent(getJLMatchObject(wspath))
    for jlStr in jlStrls:
        jlStrkeys.append(getnormalizeweigth(jlStr, False))
    # print('set jl keys length....', len(jlStrkeys))

    # 遍历法条
    for i in range(len(ftnrls)):
        # 加入法条data
        ftdata_ss = []
        ftdata_jl = []

        ftnr = ftnrls[i]
        ftmc = ftmcls[i]

        print('ftnr',ftnr)

        #加载该法条的lda模型
        # ft_corpus = '../LDAmodel/source/corpus/'+ftmc+'.txt'
        # ft_model = '../LDAmodel/source/model/'+ftmc+'_lda.model'
        # if os.path.exists(ft_model):
        #     dictionary,lda = getLDAmodel(ft_corpus,ft_model)

        ftnrArra = cutcontent(ftnr)


        this_ftkeys = getftkeys(ftmc)


        # 优化，将nr对应的keys先算好，存进dict中
        nrkeysdict = {}
        allftkeys = []
        for nr in ftnrArra:
            keys, weights = getnormalizeweigth(nr, True)
            print(keys)
            nrkeysdict[nr] = [keys, weights]
            #
            # if len(keys) >=4:
            #     allftkeys.extend([keys[3]])
            if len(keys) >=3:
                allftkeys.extend([keys[2]])
            if len(keys) >=2:
                allftkeys.extend([keys[1]])
            elif len(keys) == 1:
                allftkeys.extend([keys[0]])

        #   对于每个事实句子都把法条sp遍历比较一遍
        # for i in range(len(wsStrkeys)):
        #     wsStrkey = wsStrkeys[i]
        #     wsStr = wsStrls[i]
        #     print('wsStr',wsStr)
        #     print('wsStrkeys',wsStrkey)
            #使用法条使用lda得出的keys=========================================
            # ftkeyflag = 0
            # for _ in allftkeys:
            #     if wsStr.count(_) > 0:
            #         ftkeyflag += 1
            #
            # if ftkeyflag >= 1:
            #     ftdata_ss.append(1)
            # else:
            #
            #     count = 0
            #     if len(this_ftkeys) > 0:
            #         for this_key in this_ftkeys:
            #             if wsStr.count(this_key) > 0:
            #                 count += 1
            #         if count > 0:
            #             if count > 5:
            #                 ftdata_ss.append(1)
            #             else:
            #                 smaxsum = distance(wsStrkey, ftnrArra, nrkeysdict, wsStr, model)
            #                 print('samxsum', smaxsum)
            #                 if smaxsum > 0.3:
            #                     ftdata_ss.append(1)
            #                 else:
            #                     ftdata_ss.append(0)
            #         else:
            #             ftdata_ss.append(0)
            #     else:
            #         smaxsum = distance(wsStrkey, ftnrArra, nrkeysdict, wsStr, model)
            #         print('samxsum', smaxsum)
            #         if smaxsum > 0.3:
            #             ftdata_ss.append(1)
            #         else:
            #             ftdata_ss.append(0)
            # 使用法条使用lda得出的keys=========================================
            # if os.path.exists(ft_model) == True:
            #     tp = predict(dictionary, lda, wsStr)
            #     print('tp',tp)
            #     if tp > 0.95:
            #         ftdata_ss.append(1)
            #     # else:
            #     #     smaxsum = distance(wsStrkey, ftnrArra, nrkeysdict, wsStr, model)
            #     #     if smaxsum > 0.2:
            #     #         ftdata_ss.append(1)
            #     #     else:
            #     #         ftdata_ss.append(0)
            #
            #     elif tp > 0.85:
            #         smaxsum = distance(wsStrkey, ftnrArra, nrkeysdict, wsStr, model)
            #         print('samxsum',smaxsum)
            #         if smaxsum > 0.2:
            #             ftdata_ss.append(1)
            #         else:
            #             ftdata_ss.append(0)
            #     else:
            #         ftdata_ss.append(0)
            #
            # else:
            #     smaxsum = distance(wsStrkey, ftnrArra, nrkeysdict, wsStr, model)
            #     print('samxsum', smaxsum)
            #     if smaxsum > 0.2:
            #         ftdata_ss.append(1)
            #     else:
            #         ftdata_ss.append(0)


            # smaxsum = distance(wsStrkey, ftnrArra, nrkeysdict, wsStr, model)
            # if smaxsum > 0.3:
            #    ftdata_ss.append(1)
            # else:
            #     ftdata_ss.append(0)


        # 对于每个结论句子都把法条sp遍历比较一遍
        for i in range(len(jlStrkeys)):
            jlStrkey = jlStrkeys[i]
            jlStr = jlStrls[i]
            smaxsum = distance(jlStrkey, ftnrArra, nrkeysdict, jlStr, model)
            if smaxsum > 0.5:
                ftdata_jl.append(1)  # error1
            else:
                ftdata_jl.append(0)

        # outputdata_ss.append(ftdata_ss)
        outputdata_jl.append(ftdata_jl)
    # 输出到法条与事实的映射list，以及法条到结论映射list
    return outputdata_jl

    # 反转输出到excel中
    # outputArra_ss = numpy.array(outputdata_ss).T
    # outputArra_jl = numpy.array(outputdata_jl).T
    # wspathsp = wspath.split('/')
    # wsname = wspathsp[len(wspathsp) - 1]
    # createx(wsname, jlStrls, ftnrls, outputArra_jl,'../data/testwsoutput_ft2jl_2')
    # createx(wsname, wsStrls, ftnrls, outputArra_ss, '../data/testwsoutput_ss2ft_2')


def getdata(excelpath, ws):
    data = []
    dirt = os.listdir(excelpath)
    for e in dirt:
        if e.find(ws.split('/')[-1]) >0:
            print('excel name',e)
            data = getexceldata(excelpath + '/' + e)
            return data
    return data


# 输入文书路径和word2vec模型
# 输出事实到法条的映射关系以及法条到结论的映射关系

def wsfx(expath, word2vecmodelpath):
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

    outputdata_ss = traversews(wspath, word2vecmodel)
    # 对数据进行处理，并计算准确率和召回率
    # print('utputdata_jl', outputdata_jl)
    print('utputdata_ss', outputdata_ss)
    output_ss = numpy.reshape(outputdata_ss, (1, len(outputdata_ss) * len(outputdata_ss[0])))[0]
    # output_jl = numpy.reshape(outputdata_jl, (1, len(outputdata_jl) * len(outputdata_jl[0])))[0]


    testdata_ss_1 = getdata(datapath)
    testdata_ss = numpy.reshape(testdata_ss_1,(1, len(testdata_ss_1) * len(testdata_ss_1[0])))[0]
    # testdata_jl_1 = getdata(datapath[1],wspath)
    # testdata_jl = numpy.reshape(testdata_jl_1,(1, len(testdata_jl_1) * len(testdata_jl_1[0])))[0]
    # jl = calculatews(output_jl, testdata_jl, flag=2)
    ss = calculatews(output_ss, testdata_ss, flag=1)
    # print('jl',jl)
    print('ss',ss)
    return ss


def countf(precision_i,recall_i):
    if precision_i + recall_i > 0:
        f_i = precision_i * recall_i * 2 / (precision_i + recall_i)
    else:
        f_i = 0
    return f_i


def wsfxMain(datapath, word2vecmodelpath):
    # f_jl = open('../data/result/data1_jl_0.35_filterkeys_5len_cx.txt', 'w', encoding='utf-8')
    # f_ss = open('../data/result/ss_ftkeys.txt', 'w', encoding='utf-8')
    dir = os.listdir(datapath)
    # namels = getexcelwslist(datapath[0])
    # precision_sum_jl,recall_sum_jl, f_value_jl= 0,0,0
    precision_sum_ss, recall_sum_ss, f_value_ss = 0, 0, 0
    for i in range(0,50):
        expath = datapath +'/'+dir[i]
        ss_i = wsfx(expath, word2vecmodelpath)
        precision_i_ss = ss_i[0]
        recall_i_ss = ss_i[1]
        precision_sum_ss += precision_i_ss
        recall_sum_ss += recall_i_ss
        f_i_ss = countf(precision_i_ss, recall_i_ss)
        f_value_ss += f_i_ss
        print(precision_i_ss,recall_i_ss,f_i_ss)
            # f_ss.write(str(precision_i_ss) + ',')
            # f_ss.write(str(recall_i_ss) + ',')
            # f_ss.write(str(f_i_ss) + '\n')

    print('calculate ave:')
    print('ss')
    print(precision_sum_ss/50 , recall_sum_ss/50 ,f_value_ss/50)

    # print('jl')
    # print(precision_sum_jl / len(namels), recall_sum_jl / len(namels))
    # f_ss.write('total:')
    # f_ss.write(str(precision_sum_ss / 50) + ',')
    # f_ss.write(str(recall_sum_ss / 50) + ',')
    # f_ss.write(str(f_value_ss / 50))
    # f_ss.close()
    #
    # f_jl.write('total:')
    # f_jl.write(str(precision_sum_jl / len(namels)) + ',')
    # f_jl.write(str(recall_sum_jl / len(namels)) + ',')
    # f_jl.write(str(f_value_jl / len(namels)))
    # f_jl.close()
    # print(outputdata_dict)


wsdictpath = '../data/testws5b'
datapath = ['/users/wenny/nju/task/测试集/文书逆向分析测试集/第二组/法条到结论/all']


# wsdictpath = '/users/wenny/nju/task/法条文书分析/2014filled/2014'
# # wsdictpath = '../data/testws'


word2vecmodelpath = '../data/2014model.model'
# wsfxMain( datapath,word2vecmodelpath)
# traversews('../data/testws/3562.xml', '../data/2014model.model')
