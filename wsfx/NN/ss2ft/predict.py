# coding: utf-8

from __future__ import print_function

import os
import tensorflow as tf
import tensorflow.contrib.keras as kr

from wsfx.NN.ss2ft.cnn_model2 import TCNNConfig, TextCNN
from wsfx.NN.preprocess import preprocess
from wsfx.util.fileop import getlines

try:
    bool(type(unicode))
except NameError:
    unicode = str

corpuspath = '/Users/wenny/PycharmProjects/wsanalyse/wsfx/NN/ss2ft/model_store/source.txt'
vocab_dir = '/Users/wenny/PycharmProjects/wsanalyse/wsfx/NN/ss2ft/model_store/vocab.txt'

save_dir = '/Users/wenny/PycharmProjects/wsanalyse/wsfx/NN/ss2ft/model_store/checkpoints/textcnn'
save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径
tensorboard_dir = '/Users/wenny/PycharmProjects/wsanalyse/wsfx/NN/ss2ft/model_store/tensorboard/textcnn'
stoplist1 = getlines('/Users/wenny/PycharmProjects/wsanalyse/wsfx/data/stopwords.txt')
stoplist2 = getlines('/Users/wenny/PycharmProjects/wsanalyse/wsfx/data/num<20words.txt')

p = preprocess(corpuspath,vocab_dir)
vocab = p.getvocab()

class CnnModel:
    def __init__(self):
        self.config = TCNNConfig()
        self.model = TextCNN(self.config)

        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess=self.session, save_path=save_path)  # 读取保存的模型

    def predict(self, input1, input2):
        # 支持不论在python2还是python3下训练的模型都可以在2或者3的环境下运行
        ssls = p.precessinput(input1,stoplist1,stoplist2)#预处理后的事实
        ftls = p.precessinput(input2,stoplist1,stoplist2)
        data_1 = [p.getwordid(vocab, word, 0) for word in ssls]
        data_2 = [p.getwordid(vocab, word, 0) for word in ftls]

        feed_dict = {
            self.model.input_x_1: kr.preprocessing.sequence.pad_sequences([data_1], self.config.seq_length_1),
            self.model.input_x_2: kr.preprocessing.sequence.pad_sequences([data_2], self.config.seq_length_2),
            self.model.keep_prob: 1.0
        }

        y_pred_cls = self.session.run(self.model.y_pred_cls, feed_dict=feed_dict)
        return y_pred_cls[0]


