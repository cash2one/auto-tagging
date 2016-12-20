#-*- encoding: utf-8 -*-
'''
Created on 2015-04-07

@author: yekeren
'''

import sys
import math
import wordseg, postag

MAX_TERMS_NUM = 2048
DEFAULT_FILE_ENCODING = 'gbk'

scw_dict = None
tag_dict = None
scw_out = None
scw_tokens = None

TFIDF_FEAT_SIZE = 120

def segInit(path = 'dict'):
    ''' init wordseg module. '''
    global scw_dict
    global tag_dict
    global scw_out
    global scw_tokens

    scw_dict = wordseg.scw_load_worddict(path + '/worddict')
    tag_dict = postag.tag_create(path + '/tagdict')
    scw_out = wordseg.scw_create_out(MAX_TERMS_NUM * 10)
    scw_tokens = wordseg.create_tokens(MAX_TERMS_NUM)
    scw_tokens = wordseg.init_tokens(scw_tokens, MAX_TERMS_NUM)
    print >> sys.stderr, 'wordseg init succ'

def idfPrintFile(filename, docs, df):
    fp = open(filename, 'w')
    fp.write(str(docs) + '\n')
    items = sorted(df.iteritems(), lambda x, y: -cmp(x[1], y[1]))
    for k, v in items:
        line = '%s\t%s\n' %(k, v)
        fp.write(line.encode(DEFAULT_FILE_ENCODING))
    fp.close()

def tokenize(text):
    ''' tokenize the specific text. '''
    if not text:
        return []
    text = text.encode('gbk')
    wordseg.scw_segment_words(scw_dict, scw_out, text, len(text), 1)
    tokens_len = wordseg.scw_get_token_1(scw_out, wordseg.SCW_WPCOMP, scw_tokens, MAX_TERMS_NUM)
    postag.tag_postag(tag_dict, scw_tokens, tokens_len)
    tokens = (item[0] for item in postag.print_tags(scw_tokens, tokens_len) if ('n' in item[1] or 'a' in item[1]))
    tokens = (item.decode('gbk').lower() for item in tokens if len(item.decode('gbk')) > 1)
    tokens = (item for item in tokens if not (item[0] >= u'a' and item[0] <= u'z'))
    return tokens

def idfCompute(corpus):
    ''' compute idf from corpus. '''
    print >> sys.stderr, 'computing idf...'
    df = {}
    docs = 0
    for text in corpus:
        if text:
            docs += 1
            for token in set(tokenize(text)):
                df[token] = df.get(token, 0) + 1
    for k, v in df.items():
        if not v > 1:
            del df[k]
    return docs, df

def idfSave(filename, docs, df):
    ''' save idf to filename. '''
    print >> sys.stderr, 'saving idf to %s...' %(filename)

    import pickle
    fp = open(filename, 'wb')
    pickle.dump(docs, fp)
    pickle.dump(df, fp)
    fp.close()

def idfLoad(filename):
    ''' load idf from filename. '''
    print >> sys.stderr, 'loading idf from %s...' %(filename)

    import pickle
    fp = open(filename, 'rb')
    docs = pickle.load(fp)
    df = pickle.load(fp)
    fp.close()
    return docs, df

def tfidfExtract(text, docs, df):
    ''' extract tf-idf feature from text. '''
    tf = {}
    for token in tokenize(text):
        tf[token] = tf.get(token, 0) + 1
    tfidf = {}
    for k, v in tf.iteritems():
        dfVal = 1.0 * df.get(k, 0)
        if dfVal > 0:
            tfidf[k] = v * math.log(docs / dfVal, 10)
    return tfidf

def featExtract(meta, docs, df):
    featList = []

    ''' extract feature of interests '''
    fois = [('actor', 'ac='), ('director', 'di='), ('editor', 'ed='), ('language', 'la='), ('area', 'ar='), ('type', 'ty=')]
    for featName, featPrefix in fois:
        items = (i.strip() for i in meta[featName].split('$$') if i.strip())
        for i in items:
            featList.append(featPrefix + i)

    ''' duration and show_time '''
    if meta['duration'].isdigit():
        duration = int(meta['duration'])
        if not duration:
            featList.append('du=unknown')
        elif duration < 1800:
            featList.append('du=short')
        elif duration < 3600:
            featList.append('du=medium')
        else:
            featList.append('du=long')
    if meta['net_show_time'][:4].isdigit():
        featList.append('st=' + meta['net_show_time'][:4])

    ''' extract tfidf feature from introduction '''
    intro = meta['intro']
    tfidf= tfidfExtract(intro, docs, df)
    tfidf = sorted(tfidf.iteritems(), lambda x, y: -cmp(x[1], y[1]))[:TFIDF_FEAT_SIZE]
    for k, v in tfidf:
        featList.append('wo=' + k)
    return featList
