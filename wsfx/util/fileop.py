import json
import os

def getlines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().split('\n')
    lines = list(filter(lambda x: str(x).strip() != '', content))
    return lines


def getjson(jsonpath):
    sslist = []
    with open(jsonpath,'r',encoding='utf-8') as f:
        try:
            jsonStr = json.load(f)
            for i in jsonStr.get('factList'):
                sslist.append(i.get('content'))
        except:
            print('Read xml ERROR!')
    return sslist


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

validatedata('../data/testdata_jl')




