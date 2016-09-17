# coding:utf8
from __future__ import division
import numpy as np
import jieba
import re
import jieba.analyse
from collections import Counter,defaultdict

file_name = 'dict/stopwords_tw.txt'
# jieba.analyse.set_stop_words(file_name)
jieba.set_dictionary('dict/dict.txt.big')
def coocurance(text,windows=3):

    word_lst = [e for e in jieba.lcut(text) if e not in STOP_WORDS]

    # print '/'.join(word_lst)
    data = defaultdict(Counter)
    for i,word in enumerate(word_lst):
        indexStart = i - windows
        indexEnd = i + windows
        if indexStart < 0:
            temp = Counter(word_lst[:windows+1+i])
            temp.pop(word)
            data[word] += temp
            # print word
        elif indexStart>=0 and indexEnd<=len(word_lst):
            temp = Counter(word_lst[i-windows:i+windows+1])
            temp.pop(word)
            data[word] += temp
            # print word
        else:
            temp = Counter(word_lst[i-windows:])
            temp.pop(word)
            data[word]+=temp
            # print word
    return data


def printDict(data):
    ''' print out dict of dict  '''
    for k,v in data.items():
        for k1,v1 in v.items():
            print k,k1,v1

def textRank(graph,d=0.85,kw_num=3,with_weight=False):
    TR = defaultdict(float,[(word,1.) for word,cooc in graph.items()]) # TextRank graph with default 1
    TR_prev = TR.copy()
    err = 1e-4
    error = 1
    iter_no = 100
    index = 1
    while (iter_no >index and  error > err):
        error = 0
        TR_prev = TR.copy()
        for word,cooc in graph.items():
            temp=0
            for link_word,weight in cooc.items():
                temp += d*TR[link_word]*weight/sum(graph[link_word].values())
                # print 'temp:',temp
            TR[word] = 1 -d + temp
            # print 'word:%s,TR:%.2f'%(word.encode('utf8'),TR[word])

            # print 'TR[{}]:{}'.format(word.encode('utf8'),TR[word])
            # print '----'
        error += (TR[word] - TR_prev[word])**2
        # print '-'*40
        # print 'keywords finding...iter_no:{},\terror:{}'.format(index,error)
        index += 1
    if with_weight:
        kw = sorted(TR.iteritems(),key=lambda (k,v):(v,k),reverse=True)
        kw = [(k,v/max(zip(*kw)[1])) for k,v in kw ][:kw_num]
    else:
        kw = [word for word,weight in sorted(TR.iteritems(),key=lambda (k,v):(v,k),reverse=True)[:kw_num]]
    return kw

def abstractTextRank(graph,d=0.85,sent_num=3,with_weight=False):
    sent_TR = defaultdict(float,[(sent,np.random.rand()) for sent,_ in graph.items()])

    err = 1e-5
    error = 1
    iter_no = 100
    index = 1
    while (iter_no >index and  error > err):
        error = 0
        sent_TR_prev = sent_TR.copy()
        for sent,cooc in graph.items():
            temp = 0
            for link_sent,weight in cooc.items():
                temp += d*sent_TR[link_sent]*weight/sum(graph[link_sent].values())
                # print 'add temp:',temp
            # print '----'
            sent_TR[sent] = 1 -d + temp
        error += (sent_TR[sent] - sent_TR_prev[sent])**2

        print 'key sentence finding...iter_no:{},\terror:{}'.format(index,error)
        index += 1
    if with_weight:
        ks = sorted(sent_TR.iteritems(),key=lambda (k,v):(v,k),reverse=True)
        ks = [(k,v/max(zip(*ks)[1])) for k,v in ks ][:sent_num]
    else:
        ks = [sent for sent,weight in sorted(sent_TR.iteritems(),key=lambda (k,v):(v,k),reverse=True)[:sent_num]]
    return ks



def sentence_coocurance(text,kw_num=3):
    ## sentence_kw :
    ## {'sen1':[word1,word2,word3],'sen2':[word2,word3,word4],
    ##  'sen3':[word1,word3,word5]}
    # sentence_kw = {'A':[1,2,3],'B':[2,3,4],'C':[1,3,5]} # test used!!
    docs = re.split(u'，|。',text)
    sentence_kw = defaultdict(list)
    for sen in docs:
        if sen == u'':
            continue
        keywords = textRank(coocurance(text,windows=5),kw_num=kw_num)
        sentence_kw[sen] = keywords

    cooc_dict = defaultdict(dict) # coocurance sentence with respect to keywords

    for sentence,kw in sentence_kw.items():
        # cooc_dict[sentence] = {sentence:0}
        temp = {}
        for sent_check, kw_check in sentence_kw.items():
            if sentence == sent_check:
                # print 'nope'
                temp[sentence] =0
                continue
            else:
                count = 0
                for word in kw:
                    if word in kw_check:
                        count+=1
                # print 'yes:\t',count
                temp[sent_check] = count
        cooc_dict[sentence] = temp
    return cooc_dict



if __name__ == '__main__':

    ## load stop words ##
    with open(file_name) as f:
        doc = f.read()
    doc = doc.decode('utf8')
    doc = re.sub('\r\n','\n',doc)
    global STOP_WORDS
    STOP_WORDS = doc.split('\n')
    #

    text = u'賣鮮花的漂亮女孩在買鮮花'
    text1 = u'''
    莫蘭蒂颱風步步逼近，中央氣象局今天表示，這是1995年以來有發布陸警的最強颱風，明天到中秋節上半天是影響最劇烈的時候。

根據中央氣象局觀測，今年第14號颱風莫蘭蒂目前位在恆春東南方約290公里海面上，以每小時21轉18公里速度向西北西轉西北進行，7級暴風半徑220公里，近中心最大風速每秒60公尺，相當於17級風。

氣象局表示，強颱莫蘭蒂的暴風圈正逐漸接近東南部近海，對台東、花蓮、恆春半島、南投、台中以南地區及澎湖構成威脅。

氣象局預報員羅雅尹說，根據目前觀測，蘭嶼已經出現16級強陣風，台東近岸也觀測到6米浪高，到了明天颱風中心通過恆春半島南部海域，大台北將受外圍環流及地形影響，將有明顯降雨和較強陣風，提醒民眾不可掉以輕心。

羅雅尹說，如果颱風路徑沒有改變，最快今晚颱風的暴風圈就會接觸到恆春半島陸地，明天一整天和15日上半天都是颱風影響台灣最劇烈的時候，預估要到15日中秋節當天傍晚後風雨才會趨緩。

羅雅尹也補充，過去曾有過比莫蘭蒂颱風強度更強的颱風出現，但是如果以實際侵台的資料看來，莫蘭蒂是1995年以來，有發布陸警的最強颱風。

氣象局同時也持續發布豪雨特報，台東縣、花蓮縣有超大豪雨；宜蘭縣、屏東縣和高雄市有大豪雨；嘉義山區及台南山區有局部大雨或豪雨，其他地區及澎湖有局部大雨發生的機率，提醒民眾注意坍方、落石、土石流及山洪爆發，沿海低窪地區應防淹水。
    '''
    text2 = u'''
    受到強颱莫蘭蒂颱風的影響，桃園球場因積水無法進行今天的比賽，風雨將持續影響到週五，而它前腳剛走，另一颱風馬勒卡也將北移，台灣將受到其外圍環流的影響，因此是否會影響到週末陳金鋒引退賽的進行，還要看週末的天氣狀況而定。

桃猿球團表示，棘手的是鋒哥引退賽必須進行在比賽後，相關活動也將在之後舉行，因此如果比賽因風雨延賽，或是打到一半比賽暫停都會影響到當天的行程。

據氣象局報導，秋颱莫蘭蒂侵台今日為風雨影響最烈的時候，而明日颱風前腳剛走，外圍環流進來，預計將會有豪大雨，球賽能否進行還要看明後兩天場地受影響程度。

桃猿方也表示，目前已經邀請陳金鋒親友，希望他們當日都能一同到場，為陳金鋒慶祝這個特別的日子。
     '''
    # windows = 3 # to specifiy the windows of coocurance matrix
    text3 = re.sub('\s+','',text1)
    # # docs = [e.strip() for e in text.splitlines()]
    # data = coocurance(text,windows=5)
    # # keywords
    # kw = textRank(data,d=0.75,kw_num=3)
    # result2 = textRank(data,d=0.75,kw_num=3,with_weight=True)
    # for text in docs:
    #     printDict(coocurance(text))

    #
    sent_graph = sentence_coocurance(text3)
    auto_abstract = abstractTextRank(sent_graph,sent_num=5,with_weight=True,d=0.3)
    # print '\n'.join(auto_abstract)
    for e,weight in auto_abstract:
        print e,weight
