import json
import os
from wsfx.util.wsfun import getFTList
from wsfx.util.wsfun import getFTfromQW
from wsfx.util.wsfun import getJLMatchObject
from wsfx.util.wsfun import getSSMatchObject
from wsfx.util.excelop import createx, getrowls, getrow2ls
import shutil

def getlinesGBK(filepath):
    with open(filepath, 'r', encoding='gbk') as f:
        content = f.read().split('\n')
    lines = list(filter(lambda x: str(x).strip() != '', content))
    return lines

def getlines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().split('\n')
    lines = list(filter(lambda x: str(x).strip() != '', content))
    return lines


def getfactjson(jsonpath):
    sslist = []
    with open(jsonpath,'r',encoding='utf-8') as f:
        try:
            jsonStr = json.load(f)
            for i in jsonStr.get('factList'):
                sslist.append(i.get('content'))
        except:
            print('Read xml ERROR!')
    return sslist


def readkeysjson(jsonpath):
    keyslist = []
    with open(jsonpath, 'r', encoding='utf-8') as f:
        try:
            jsonStr = json.load(f)
            print(jsonStr)
            for i in jsonStr:
                keyslist.append(i.get('name'))
        except:
            print('Read xml ERROR!')
    return keyslist

def writejson(dict,jsonpath):
    json.dump(dict,jsonpath,ensure_ascii=False)



def validatedata(wsdictpath):
    dir = os.listdir(wsdictpath)
    for ws in dir:
        wspath = wsdictpath+'/'+ws
        content = ''
        with open(wspath,'r',encoding='utf-8') as f:
            content = f.read()
        sum = content.count('!@#')
        s1 = content.count('!@#1')
        s2 = content.count('!@#0')
        s3 = content.count('!@#2')
        if sum/3==s1+s2:
            pass
        else:
            print(ws)
            print(sum)
            print(s1)
            print(s2)
            print(s3)

def getftname(ftmc):
    if ftmc.find('《') > 0:
        startindex = str(ftmc).index('《')
    else:
        startindex = 0
    if ftmc.find('条') > 0:
        sub = str(ftmc)[startindex:str(ftmc).index('条')]
    elif ftmc.find('款') > 0:
        sub = str(ftmc)[startindex:str(ftmc).index('款')]
    else:
        sub = str(ftmc)[startindex:]
    return sub

# #计算文书集中的法条分布
def countftfb(dictdir):
    p_dir = os.listdir(dictdir)
    #全局变量
    sum = 0
    dict = {}
    ftlist = []
    for p in p_dir:
        p_path = dictdir+ '/'+ p
        if os.path.isdir(p_path):#判断是否是目录
            dir = os.listdir(p_path)
            print('dict size', len(dir))
            sum += len(dir)  #统计个数

            for ws in dir:
                if ws.find('Store') > -1:
                    continue
                wspath = p_path + '/' + ws
                # ftmcls , ftnrcls = getFTList(wspath)
                ftmcls = getFTfromQW(wspath)
                for ftmc in ftmcls:
                    # nums = str(ftmc).count('第')
                    if ftmc.find('《') > 0:
                        startindex = str(ftmc).index('《')
                    else:
                        startindex = 0
                    if ftmc.find('条') > 0:
                        sub = str(ftmc)[startindex:str(ftmc).index('条')]
                    elif ftmc.find('款') > 0:
                        sub = str(ftmc)[startindex:str(ftmc).index('款')]
                    else:
                        sub = str(ftmc)[startindex:]
                    if sub in ftlist:
                        dict[sub] += 1
                    else:
                        dict[sub] = 1
                    ftlist.append(sub)

    ftls = list(set(ftlist))
    count = []
    for x in ftls:
        count.append([dict[x]/sum*100])
    rows = ftls
    cols = ['百分比']
    data = count
    createx(dictdir.split('/')[-1],rows,cols,data,'../data/法条统计')


#将文件按照文件夹中的序号重命名
def renamedictfiles(dictpath):
    dir = os.listdir(dictpath)
    for i in range(len(dir)):
        ws = dir[i]
        wspath = dictpath + '/' + ws
        if i < 10:
            newname = dictpath+'/00'+ str(i) + '_'+ws
        elif i <100:
            newname = dictpath + '/0' + str(i)+'_'+ws
        elif i < 1000:
            newname = dictpath + '/' + str(i) +'_'+ws
        os.rename(wspath,newname)


#寻找文书集中引用了某法条的文书
def findft(dictpath):
    dir = os.listdir(dictpath)
    for i in range(len(dir)):
        ws = dir[i]
        wspath = dictpath + '/' + ws
        ftmcls,ftnrls = getFTList(wspath)
        for ft in ftmcls:
            if ft.find('《中华人民共和国刑事诉讼法》的解释第五百零五条') > 1:
                 print(ws)


def txttestset(dictpath,output):
    dir = os.listdir(dictpath)
    content = ''
    for i in range(len(dir)):
        ws = dir[i]
        wspath = dictpath + '/' + ws
        ftls = getFTfromQW(wspath)
        ssls = getSSMatchObject(wspath)
        jlls = getJLMatchObject(wspath)
        content += ws +'end!fact:'
        content += '!@#'.join(ssls)
        content += 'end!ft:'
        content += '!@#'.join(ftls)
        content += 'end!jl:'
        content += '!@#'.join(jlls)
        content += '\n'
    with open(output, 'w', encoding='utf-8') as f:
        f.write(content)

def getexcelwslist(exceldictpath):
    dir = os.listdir(exceldictpath)
    namels = []
    for e in dir:
        namels.append(e.split('_')[1])

    return namels


#从法条关键词txt中获取对应法条的所有关键词
def getftkeys(ft):
    content = open('../LDAmodel/result/topic_allft.txt','r',encoding='utf-8').read().split('\n')
    for line in content:
        sp = line.split(':')
        ftname = sp[0]
        if ftname == ft:
            if sp[1] == '':
                keys = []
            else:
                keys = list(filter(lambda  x:x.strip()!='' ,sp[1].split(',') ))
    return keys


def gettyc(word,tycsp):

    for sp in tycsp:
        if sp.count(' '+word+' ') > 0:
            return list(sp.split(' ')[1:])
    return [word]


def filterws(dictdir):
    allft = getrowls('../data/法条统计/'+ dictdir.split('/')[-1]+'_20180613.xls')
    allpre = getrow2ls('../data/法条统计/'+ dictdir.split('/')[-1]+'_20180613.xls')
    #建立高频法条集合
    ftlist = []
    mer = zip(allft,allpre)
    for ft,pre in mer:
        if float(pre) > 0.1:
            ftlist.append(ft)
    count = 0
    p_dir = os.listdir(dictdir)
    filter_path = dictdir+'/'+'过滤'
    if not os.path.exists(filter_path):
        os.mkdir(filter_path)
    for p in p_dir:
        p_path = dictdir + '/' + p
        if os.path.isdir(p_path):  # 判断是否是目录
            dir = os.listdir(p_path)
            for ws in dir:
                if ws.find('Store') > -1:
                    continue
                wspath = p_path + '/' + ws
                ftmcls = getFTfromQW(wspath)
                for ftmc in ftmcls:
                    ft = getftname(ftmc)
                    if ft in ftlist:
                        pass
                    else:#如果该文书包含低频法条，过滤掉，并跳出法条遍历循环
                        shutil.move(wspath,filter_path)
                        count += 1
                        break
    print(count)




# txttestset('../data/testws5b','../data/交通肇事测试集.txt')

# findft('/users/wenny/nju/task/法条文书分析/2014filled/2014')
# renamedictfiles('../data/1w篇_事实到法条')
# renamedictfiles('../data/1w篇_法条到结论')
# countftfb('/users/wenny/nju/task/法条文书分析/故意杀人罪/2014')

# countftfb('../data/testws5b')

# validatedata('../data/testdata_jl')

# readkeysjson('../data/交通肇事罪.json')


#对各个案由过滤文书
# dictpath = '/users/wenny/nju/task/文书整理'
# dir = os.listdir(dictpath)
# for d in dir:
#     print(d)
#     d_path = dictpath+'/'+d
#     if os.path.isdir(d_path):
#         if d_path.find('盗窃罪') > -1 or d_path.find('信用卡诈骗') > -1 or d_path.find('强奸罪') > -1:
#             pass
#         else:
#             print('filter start>>')
#             filterws(d_path)
#             print('filter end..')


# #对各个案由过滤错的文书重新提取出来
def checkwsft():
    dictpath = '/users/wenny/nju/task/文书整理'
    dir = os.listdir(dictpath)
    for d in dir:  # 当前是案由目录
        d_path = dictpath + '/' + d
        if not os.path.isdir(d_path):
            continue
        if d == 'WriterR':
            continue
        print(d)
        allft = getrowls('../data/法条统计/' + d + '_20180613.xls')
        allpre = getrow2ls('../data/法条统计/' + d + '_20180613.xls')
        # 建立高频法条集合
        ftlist = []
        mer = zip(allft, allpre)
        for ft, pre in mer:
            print(pre, int(pre))

            # if pre > 0.1:
            #     ftlist.append(ft)
        count = 0

        if os.path.isdir(d_path):
            d_childdir = os.listdir(d_path)
            newfilter_path = d_path + '/newfilter'
            if not os.path.exists(newfilter_path):
                os.mkdir(newfilter_path)
            print(newfilter_path)
            for d_childd in d_childdir:  # 当前是案由子目录
                d_child_path = d_path + '/' + d_childd
                if d_childd == '过滤':  # 当前是过滤目录
                    d_filterdir = os.listdir(d_child_path)
                    print(d_child_path)
                    for ws in d_filterdir:
                        wspath = d_child_path + '/' + ws
                        ftmcls = getFTfromQW(wspath)
                        for ftmc in ftmcls:
                            ft = getftname(ftmc)
                            if ft in ftlist:
                                pass
                            else:  # 如果该文书包含低频法条，过滤掉，并跳出法条遍历循环
                                # shutil.move(wspath, newfilter_path)
                                count += 1
                                break
                    break
        print(count)



#将文书加上其案由前缀
def wsname_an():
    dictpath = '/users/wenny/nju/task/文书整理/剩余'
    dir = os.listdir(dictpath)
    for an in dir:  # 当前是案由目录
        an_path = dictpath + '/' + an
        if an == 'whole' or an == '.DS_Store':
            pass
        else:
            andir = os.listdir(an_path)
            for ws in andir:
                if ws == '.DS_Store':
                    pass
                else:
                    wspath = dictpath + '/' + an + '/' + ws
                    os.rename(wspath, dictpath + '/' + an + '_' + ws)
                    shutil.move(dictpath + '/' + an + '_' + ws, dictpath + '/whole')
















