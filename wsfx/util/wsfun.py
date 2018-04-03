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

def getZKDL(path):
    content = ''
    qw = getQW(path)
    for qwchild in qw:
        if qwchild.tag == 'AJJBQK':
            for ajjbqkchild in qwchild:
                if ajjbqkchild.tag == 'ZKDL':
                    content = ajjbqkchild.attrib['value']
    return content

def getFTList(path):
    ftnamelist = []
    ftnrlist = []
    qw = getQW(path)
    for qwchild in qw:
        if qwchild.tag == 'YYFLNR':
            for yyflfzchild in qwchild:
                if yyflfzchild.tag == 'FLNRFZ':
                    for flnrfzchild in yyflfzchild:
                        flag= 0
                        if flnrfzchild.tag == 'FLMC':
                            flmc = flnrfzchild.attrib['value']
                            flag += 1
                        if flnrfzchild.tag == 'FLNR':
                            flnr = flnrfzchild.attrib['value']
                            flag += 2
                        if flag==2 and flmc and flnr and flnr !='NOT FOUND':
                            ftnamelist.append(flmc)
                            ftnrlist.append(flnr)
    return ftnamelist,ftnrlist




