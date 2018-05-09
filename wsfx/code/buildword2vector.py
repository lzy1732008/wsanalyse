#输入法条的关键词，使用word2vec获取法条关键词的同义词，注意:输入文书作为语料库，用文书的QW内容
import os
import jieba.posseg as pos
import gensim
from gensim.models import word2vec
from wsfx.util.wsfun import getQW
from wsfx.util.wsfun import getFTList
from wsfx.util.fileop import getlines


def buildmodel(wspath,corpuspath,modelpath,spwordpath):
    print('build model......')
    setCor(wspath,corpuspath,spwordpath)
    print('start.....')
    sentence = word2vec.LineSentence(corpuspath)
    model = word2vec.Word2Vec(sentence,min_count=5,size = 200)
    print('saveing.....')
    model.save(modelpath)
    print('built......')
    print('end....')


#将全文中指定词性的词删除
def filterwordwithcx(cutre,cxlist,spwordpath):
    wordlist = []
    print('filterword....')
    stopwords = getlines(spwordpath)
    for (w,k) in cutre:
        if k not in cxlist and w not in stopwords:
            wordlist.append(w)
    return wordlist

def setCor(dicpath,corpuspath,spwordpath):
    print('setCor:'+dicpath)
    filepathlist = os.listdir(dicpath)
    index = 0
    cxlist = ['x','p','nr','uj']
    with open(corpuspath,'w',encoding='UTF-8') as f:
        for filepath in filepathlist:
            print('index', index)
            index += 1
            ftmclist,ftnrlist = getFTList(dicpath + '\\' + filepath)
            ftnr = '。'.join(ftnrlist)
            content = getQW(dicpath + '\\' + filepath).attrib['value']+ftnr
            contentcut = pos.cut(content)
            content_filter = filterwordwithcx(contentcut, cxlist, spwordpath)
            for word in content_filter:
                f.write(word+' ')
            f.write('\n')

def load_models(model_path):
    return gensim.models.Word2Vec.load(model_path)

if __name__=='__main__':
    # ws_path='D:\\nju\\study\\task\\文书逆向分析\\法条内容填充2014\\2014'
    # corpus_path = '../data/2014corpus.txt'
    model_path='../data/2014model.model'
    # stopwordspath = '../data/stopwords.txt'
    # buildmodel(ws_path,corpus_path,model_path,stopwordspath)
    model = load_models(model_path)
    # similary_words = model.most_similar(u'死亡', topn=30)
    # print(similary_words)
    ls = model['死亡']
    s = 0
    for n in ls:
        s +=n
    print(s/len(ls))

    ls = model['受伤']
    s = 0
    for n in ls:
        s += n
    print(s / len(ls))


