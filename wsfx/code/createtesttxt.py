from wsfx.code.fxws import getSSMatchObject
from wsfx.code.fxws import getJLMatchObject
from wsfx.util.wsfun import getFTList
from wsfx.util.contentop import cutcontent
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


allwsdict = '/users/wenny/nju/task/法条文书分析/2014filled/2014'
testwsdict = '../data/testws'
testdata = '../data/testdata_jl'
dir = os.listdir(allwsdict)

# resultList = random.sample(range(0, 40000), 20);
# for i in resultList:
#     wsname = dir[i]
#     src = allwsdict + '/' + wsname
#     target = testwsdict +'/' + wsname
#     shutil.copy(src,target)


dir = os.listdir(testwsdict)
for wsname in dir:
    print(wsname)
    wspath = testwsdict + '/' + wsname
    wstestpath = testdata + '/' + wsname.split('.')[0] + '.txt'
    if wsname.endswith('.xml'):
       createtest(wspath, wstestpath)
