# -*- coding=utf-8 -*-

import os
import pdb
import copy
import time
import collections
from typing import List, Dict, Union, Any

import pkuseg
import jionlp as jio
from jionlp import logging
#from jionlp.gadget


def analyse_freq_words(dataset_x: List[List[str]], dataset_y: List[Any],
                       min_word_freq=10, min_word_threshold=0.8):
    ''' 采用朴素贝叶斯的方式，分析文本分类语料中，各个类别的高频特征词汇，用于制作类型词典，
    分析完毕后，方便加入模型当中，形成有效的模型和规则词典相结合的模型，提高模型的稳定性以及
    F1 值。
    
    Args:
        dataset_x: 分词、停用词处理后的词汇列表
        dataset_y: 文本对应的标签类型
        min_word_freq: 最小词频，若语料中词频小于 min_word_freq，则不予考虑其分布
        min_word_threshold: 每个类别返回高频特征词最低阈值。
    
    Return:
        Dict[Dict[str, List[int, float]]]: 各个类别对应的高频特征词汇，以及其统计词频
            和概率。
    
    Examples:
        >>> import jieba
        >>> import jionlp as jio
        >>> dataset_x = ['房间比较差，挺糟糕的，尤其是洗手间。', 
                         '真糟糕！连热水都没有。',
                         '价格比比较不错的酒店。']
        >>> dataset_y = ['负', '负', '正']
        >>> dataset_x = [jieba.lcut(text) for text in dataset_x]  # 采用任何分词器处理均可
        >>> dataset_x = [jio.remove_stopwords(text_segs) for text in dataset_x]  # 去停用词
        >>> result = jio.text_classification.analyse_freq_words(
            ... dataset_x, dataset_y, min_word_freq=1)
        
        {
            '负': {
                '糟糕': [2, 1.0],
                '没有': [1, 1.0],
                '差': [1, 1.0]
            }, 
            '正': {
                '不错': [1, 1.0]
            }
        }
    
    '''
    # 统计分类类型
    class_list = list(set(dataset_y))
    logging.info('当前包含的类型包括：{}'.format(class_list))
    
    # 统计词汇数量和词频
    word_list = list()
    for item in dataset_x:
        word_list.extend(item)
    word_dict = dict([item for item in collections.Counter(word_list).most_common()
                      if item[1] >= min_word_freq])
    
    # 统计各词在各类别中占比
    tmp_word_dict = dict([tuple([word, [0, 0]])for word in word_dict])
    class_words_statistics = dict()
    for _class in class_list:
        class_words_statistics.update(
            {_class: copy.deepcopy(tmp_word_dict)})
    
    for text_segs, label in zip(dataset_x, dataset_y):
        for word in text_segs:
            if word in word_dict:
                class_words_statistics[label][word][0] += 1
            
    result = dict()
    for label, words_statistics in class_words_statistics.items():
        for word, stats in words_statistics.items():
            stats[1] = stats[0] / word_dict[word]
        sorted_result = sorted(
            [item for item in words_statistics.items() if item[1][1] > min_word_threshold],
            key=lambda i:i[1][1], reverse=True)
        result.update({label: dict(sorted_result)})
            
    pdb.set_trace()
    return result






if __name__ == '__main__':
    
    import random
    content = jio.read_file_by_line(
        '/data1/ml/cuichengyu/dataset_store/ChnSentiCorp_htl_all.csv')[1:]
    #content.extend(jio.read_file_by_line(
    #    '/data1/ml/cuichengyu/dataset_store/waimai.csv')[1:])
    random.shuffle(content)
    content = content[:1000]
    dataset_x = [item.split(',', 1)[1] for item in content]
    dataset_y = [item.split(',', 1)[0] for item in content]
    
    #'''
    pku_obj = pkuseg.pkuseg()
    #'''
    dataset_x = [jio.remove_stopwords(
        pku_obj.cut(''.join(text)), 
        remove_time=True, remove_location=True, remove_number=True, remove_non_chinese=True,
        save_negative_words=True)
        for text in dataset_x]

    dataset_x = ['房间比较差，尤其是洗手间。', 
                         '真糟糕！连热水都没有。',
                         '价格比比较不错的酒店。']
    dataset_y = ['负', '负', '正']
    #dataset_x = train_x + valid_x + test_x
    #dataset_y = train_y + valid_y + test_y
    res = analyse_freq_words(dataset_x, dataset_y, min_word_freq=1)
    print(res)
    pdb.set_trace()





