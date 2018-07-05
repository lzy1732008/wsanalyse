from wsfx.code.fxws import getSSMatchObject
from wsfx.code.fxws import getJLMatchObject
from wsfx.util.wsfun import getFTfromQW,getFTList,getZJ
from wsfx.util.contentop import cutcontent
from wsfx.util.excelop import createx
import os
import random
import shutil

def createtest(wspath, wstestpath):
    ftmcls, ftnrls = getFTList(wspath)
    wsStrls = cutcontent(getJLMatchObject(wspath))

    with open(wstestpath, 'w', encoding='utf-8') as f:
        for i in range(len(ftmcls)):

            for wsStr in wsStrls:
                line = []
                line.append(ftmcls[i])
                line.append(ftnrls[i])
                line.append(wsStr)
                f.write('!@#'.join(line))
                f.write('\n')


# 随机选取文书，然后转换成事实法条Excel标注，再用这个代码还需再检查逻辑
def create_ftset_ex():
    allwsdict = '/users/wenny/nju/task/法条文书分析/故意杀人罪/2014'
    allwsdict = '/盗窃罪'
    testwsdict = '../data/testjtzs1w'
    testdata = '../data/1w篇_事实到法条'
    dir = os.listdir(allwsdict)

    print(len(dir))
    resultList = random.sample(range(0, 40000), 10000);
    for i in resultList:
        wsname = dir[i]
        src = allwsdict + '/' + wsname
        target = testwsdict + '/' + wsname
        shutil.copy(src, target)

    dir = os.listdir(testwsdict)
    for wsname in dir:
        print(wsname)
        wspath = testwsdict + '/' + wsname
        # wstestpath = testdata + '/' + wsname.split('.')[0] + '.txt'
        if wsname.endswith('.xml'):
            ftmcls, ftnrls = getFTList(wspath)
            zipob = zip(ftmcls, ftnrls)
            cols = []
            for ftmc, ftnr in zipob:
                cols.append(str(ftmc) + ':' + str(ftnr))
            wsStrls = cutcontent(getSSMatchObject(wspath))
            createx(wsname, wsStrls, cols, [], testdata)


#生成证据事实标记表格
def create_zjset_ex(testwsdict,expath):
    dir = os.listdir(testwsdict)
    index = 0
    for wsname in dir:
        print(index)
        index += 1
        wspath = testwsdict+'/'+wsname
        if str(wsname).endswith('.xml'):
            zjlist = getZJ(wspath)
            wsStrls = cutcontent(getSSMatchObject(wspath))
            createx(wsname,wsStrls,zjlist,[],expath)






def txttestset(dictpath,output):
    dir = os.listdir(dictpath)
    content = ''
    for i in range(len(dir)):
        ws = dir[i]
        wspath = dictpath + '/' + ws
        ftls = getFTfromQW(wspath)
        ssls = cutcontent(getSSMatchObject(wspath))
        jlls = cutcontent(getJLMatchObject(wspath))
        content += ws +'end!fact:'
        content += '!@#'.join(ssls)
        content += 'end!ft:'
        content += '!@#'.join(ftls)
        content += 'end!jl:'
        content += '!@#'.join(jlls)
        content += '\n'
    with open(output, 'w', encoding='utf-8') as f:
        f.write(content)

# txttestset('../data/testws1w','../data/交通肇事测试集.txt')

create_zjset_ex('../data/testws5b','../data/zjex5b')