import lxml.etree

def getQW(path):
    tree = lxml.etree.parse(path)
    root = tree.getroot()
    for qw in root:
        return qw

def getRDSS(path):
    content = ''
    qw = getQW(path)
    for qwchild in qw:
        if qwchild.tag == 'AJJBQK':
            for ajjbqkchild in qwchild:
                if ajjbqkchild.tag == 'BSSLD':
                    for bssldchild in ajjbqkchild:
                        if bssldchild.tag == 'ZJXX':
                            for zjxxchild in bssldchild:
                                if zjxxchild.tag == 'ZJFZ':
                                    for zjfzchild in zjxxchild:
                                        if zjfzchild.tag == 'RDSS':
                                            content = zjfzchild.attrib['value']
    return content
#指控段落
def getZKDL(path):
    content = ''
    qw = getQW(path)
    for qwchild in qw:
        if qwchild.tag == 'AJJBQK':
            for ajjbqkchild in qwchild:
                if ajjbqkchild.tag == 'ZKDL':
                    content = ajjbqkchild.attrib['value']
    return content

#从新填充了法条内容的文书里提取法条列表
def getFTList(path):
    ftnamelist = []
    ftnrlist = []
    qw = getQW(path)
    for qwchild in qw:
        if qwchild.tag == 'YYFLNR':
            for yyflfzchild in qwchild:
                if yyflfzchild.tag == 'FLNRFZ':
                    for flnrfzchild in yyflfzchild:
                        flag = 0
                        if flnrfzchild.tag == 'FLMC':
                            flmc = flnrfzchild.attrib['value']
                            flag += 1
                        if flnrfzchild.tag == 'FLNR':
                            flnr = flnrfzchild.attrib['value']
                            flag += 2
                        if flag == 2 and flmc and flnr and flnr != 'NOT FOUND':
                            ftnamelist.append(flmc)
                            ftnrlist.append(flnr)

    return ftnamelist,ftnrlist

#文书QW下面的节点内容获取,如文首、诉讼情况、案件基本情况、裁判分析过程、判决结果这几个的value

def getQWChildContent(path,childname):
    content = ''
    qw = getQW(path)
    for qwchild in qw:
        if qwchild.tag == childname:
            content += qwchild.attrib['value']

    return content



