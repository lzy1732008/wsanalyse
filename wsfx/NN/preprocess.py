import tensorflow.contrib.keras as kr
import numpy as np
import jieba.analyse as ana
import jieba.posseg as pos
from wsfx.util.fileop import getlines

class preprocess():
    def __init__(self,corpuspath,vocabpath):
        self.corpuspath = corpuspath
        self.vocabpath = vocabpath

    def setvocab(self):
        ft_len = 0
        ss_len = 0
        num = 0
        vocab = []
        f = open(self.corpuspath, 'r', encoding='utf-8')
        lines = f.read().split('\n')
        for line in lines:
            if line.strip() != '':
                ss = (line.split('|'))[1]
                ssls = ss.split(' ')
                for word in ssls:
                    if not word in vocab:
                        vocab.append(word)

                ft = (line.split('|'))[0]
                ftls = ft.split(' ')
                for word in ftls:
                    if not word in vocab:
                        vocab.append(word)

                ft_len += len(ftls)
                ss_len += len(ssls)
                num += 1

        f.close()
        f = open(self.vocabpath, 'w', encoding='utf-8')
        f.write(' '.join(vocab))
        f.close()
        print(ft_len / num, ss_len / num)

    # setvocab()

    def idtoword(idls, vocab):
        words = []
        for id in idls:
            print(id)
            words.append(list(vocab)[int(id)])
        return words

    def getvocab(self):
        f = open(self.vocabpath, 'r', encoding='utf-8')
        vocab = list(filter(lambda x: str(x).strip() != '', f.read().split(' ')))
        return vocab

    def getwordid(self,vocab, word,flag):
        if word in vocab:
            return list(vocab).index(word)
        else:
            return len(vocab)

    # 返回padding好的输入和输出
    def processfile(self,vocab, max_length_1, max_length_2):
        num1 = 0
        num2 = 0
        f = open(self.corpuspath, 'r', encoding='utf-8')
        lines = f.read().split('\n')
        data1 = []
        data2 = []
        output = []
        for line in lines:
            if line.strip() != '':
                ftls = (line.split('|'))[0].split(' ')
                ssls = (line.split('|'))[1].split(' ')
                label = (line.split('|'))[2]

                if label.strip() == '0.0':
                    if num1 % 2 == 0:
                        data1.append([self.getwordid(vocab, word) for word in ssls])
                        data2.append([self.getwordid(vocab, word) for word in ftls])
                        output.append([1, 0])
                    num1 += 1

                elif label.strip() == '1.0':
                    data1.append([self.getwordid(vocab, word) for word in ssls])
                    data2.append([self.getwordid(vocab, word) for word in ftls])
                    output.append([0, 1])
                    num2 += 1
        data1_pad = kr.preprocessing.sequence.pad_sequences(data1, max_length_1)
        data2_pad = kr.preprocessing.sequence.pad_sequences(data2, max_length_2)
        print(num1, num2)
        print(len(data1), len(data2))
        return np.array(data1_pad), np.array(data2_pad), np.array(output)

    def precessinput(self, input, stoplist1, stoplist2):
        words = pos.cut(input)
        sls = []
        for word, cx in words:
            if cx == 'n' or cx == 'v' or cx == 'a':
                if word in stoplist1 or word in stoplist2:
                    pass
                else:
                    sls.append(word)
        return sls


# p = preprocess('ft2jl/model_store/source.txt','ft2jl/model_store/vocab.txt')
# vocab = p.getvocab()
# print(len(vocab))
# # processfile(vocab,30,50)