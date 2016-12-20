#coding: utf-8

import os, sys
import traceback
import wordseg, postag, wordner, wordrank

SEG_WPCOMP = wordseg.SCW_WPCOMP
SEG_BASIC  = wordseg.SCW_BASIC

SEG_DEFAULT   = SEG_WPCOMP

class Tokenizer():
    def __init__(self):
        print >> sys.stderr, "WordSegUtil constructed"
        self.maxTermCount = 2048
        dict_ab_url=(os.path.dirname(os.path.abspath(__file__)))+"/dict"
        #print dict_ab_url
        # 加载词典
        #print os.path.join(dict_ab_url, "worddict")
        self.hWordDict = wordseg.scw_load_worddict(os.path.join(dict_ab_url, "worddict"))
        self.hTagDict  = postag.tag_create(os.path.join(dict_ab_url, "tagdict"))
        # hNerDict  = wordner.ner_dict_load(os.path.join(dict_ab_url, "nerdict"))
        self.hRankDict = wordrank.wdr_create(os.path.join(dict_ab_url, "rankdict"))

        self.hScwOut = wordseg.scw_create_out(self.maxTermCount * 10)
        # hNerOut = wordner.ner_out_create(hNerDict, self.maxTermCount)
        self.hRanks  = wordrank.create_ranks(self.maxTermCount)

        # token
        self.hTokens  = wordseg.create_tokens(self.maxTermCount)
        self.hTokens  = wordseg.init_tokens(self.hTokens, self.maxTermCount)

        # 专名过滤
        self.nerWhiteTags = set([
                "PER",          # 人名
                #"LOC",          # 地名
                #"ORG",          # 机构
                #"SFT",          # 软件
                "GME",          # 游戏
                "SNG",          # 歌曲
                #"NVL",          # 小说
                "VDO",          # 视频
                "BRD",          # 品牌
                "CTN",          # 动漫
                "VDO_MVE",      # 电影
                "VDO_TV",       # 电视剧
                "VDO_TVSHOW"    # 电视节目
            ])


    def __del__(self):
        wordrank.destroy_ranks(self.hRanks)
        wordseg.destroy_tokens(self.hTokens)

        # wordner.ner_out_destroy(Tokenize.hNerOut)
        wordseg.scw_destroy_out(self.hScwOut)

        wordrank.wdr_destroy(self.hRankDict)
        # wordner.ner_dict_destroy(Tokenize.hNerDict)
        postag.tag_destroy(self.hTagDict)
        wordseg.scw_destroy_worddict(self.hWordDict)

        print >> sys.stderr, "Tokenize destroied"
        

    def tokenize_string(self, text, coding="utf8",segType = SEG_DEFAULT):
        ret={
            "error":0,
            "reason":"",
            "ret":[],
            "text":text
            }
        try:
            if coding=="utf8":
                text=text.decode("utf8").encode("gbk")
            elif coding=='unicode':
                text = text.encode('gbk')
            segRes = []
        # 切词
            if len(text) == 0 or not isinstance(text,str):
                return ret
            wordseg.scw_segment_words(self.hWordDict, self.hScwOut, text, len(text), 1)
            # 你妹的,错误中文编码会在这里抛异常
            # if 0 > wordseg.scw_segment_words(Tokenize.hWordDict, Tokenize.hScwOut, text, 1):
            #     ret["error"]=1
            #     ret["reason"]="scw_segment_words failed"
            #     return ret
        except Exception, e:
            ret["error"]=1
            ret["reason"]="scw_segment_words failed"
            return ret

        tokensLen = wordseg.scw_get_token_1(self.hScwOut, segType, self.hTokens, self.maxTermCount)
        tokensList = wordseg.tokens_to_list(self.hTokens, tokensLen)

        # 专名识别
        # if 0 > wordner.ner_tag(Tokenize.hNerDict, Tokenize.hTokens, tokensLen, Tokenize.hNerOut, langid):
        #     print >> sys.stderr, "WARNING: ner_tag failed"
        #     return segRes, nerRes
        #
        # gran = 2
        # nerRes = wordner.get_tag_list(Tokenize.hNerOut, Tokenize.hTokens, tokensLen, gran)
        # nerRes = [ (term, wordner.get_type_name(Tokenize.hNerDict, langid, nerTag)) for term, nerTag in nerRes ]
        # nerRes = [ (term, nerTag) for term, nerTag in nerRes if nerTag in Tokenize.nerWhiteTags ]

        #tokensLen = wordrank.get_nertokens(Tokenize.hScwOut, Tokenize.hNerOut, Tokenize.hTokens, Tokenize.maxTermCount)
        #tokensList = wordseg.tokens_to_list(Tokenize.hTokens, tokensLen)

        # 词性标注
        tokensLen = postag.tag_postag(self.hTagDict, self.hTokens, tokensLen)
        postagRes = postag.print_tags(self.hTokens, tokensLen)

        position = 0
        for token, pos in postagRes:
            token = token.decode('gbk', 'ignore')
            segRes.append([token, pos, position])
            position += len(token)
        ret["ret"]=segRes
        #return segRes
        return ret

if __name__=="__main__":
    #test_str = '无间道的前世今生...吴镇宇实在是太有味道了...但这不是一部好电影, 真是不能忍'
    test_str = '狼图腾'
    tokenizer = Tokenizer()
    r=tokenizer.tokenize_string(test_str)
    # for k, v in r.items():
    #     print '%s\t%s' % (k, v)
    for e in r["ret"]:
        print '%s\t%s\t%s' % (e[0].encode('utf8'), e[1], e[2])
        #print '\t'.join(map(lambda x: str(x).encode('utf8'), e))
