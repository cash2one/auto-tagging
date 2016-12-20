#coding: utf-8
import sys
sys.path.append('..')
from Config import Config
import os
from Tokenize import Tokenize
from Feature import Feature
from DAL.DoubanComment import DoubanComment

entity_dict = {
        u'影片整体质量': [u'本片', u'这部', u'此片', u'片子', u'电影', u'这一部'],
        u'剧情': [u'情节', u'剧情', u'故事', u'主线'],
        u'配乐': [u'配乐', u'音乐', u'背景音乐'],
        u'特效': [u'特效', u'效果']
        }

# entity_dict_unicode = {}
# for entity, keywords in entity_dict.items():
#     entity_unicode = entity.decode('utf8')
#     entity_dict_unicode[entity] = []
#     for keyword in keywords:
#         keyword_unicode = keyword.decode('utf8')
#         entity_dict_unicode[entity].append(keyword_unicode)

junction_dict = {
        'director': u'导的',
        'actor': u'演的',
        'general': ''
        }

opinion_dict = {
        1: u'很棒',
        -1: u'真烂'
        }


class Classify():
    def __init__(self):
        self.positive_cnt = 0
        self.negtive_cnt = 0
        self.positivie_token_dict = {}
        self.negtive_token_dict = {}
        for opinion in ['positive', 'negtive']:
            self.load_possibility(opinion)

        self.director_dict = {}
        self.actor_dict = {}
        self.load_person()

    def load_possibility(self, opinion='positive'):
        if opinion is 'positive':
            rating = 50
        else:
            rating = 10
        input_obj = open(os.path.join(Config.opinion_path, str(rating)))
        with input_obj:
            comment_cnt = int(input_obj.readline().strip())
            token_dict = {}
            for line in input_obj:
                fields = line.strip().split('\t')
                token = fields[0].decode('utf8')
                possibility = (float(fields[1]) + 1)/comment_cnt
                token_dict[token] = possibility

        if opinion is 'positive':
            self.positive_cnt = comment_cnt
            self.positivie_token_dict = token_dict
        else:
            self.negtive_cnt = comment_cnt
            self.negtive_token_dict = token_dict

    def saperate_name(self, name):
        name_parts = name.split('·')
        name_parts = map(lambda x: x.decode('utf8'), name_parts)
        long_name_parts = filter(lambda x: len(x) > 1, name_parts)
        return long_name_parts

    def load_person(self):
        input_obj = open(Config.person_path)
        with input_obj:
            for line in input_obj:
                fields = line.strip('\n').split('\t')
                try:
                    douban_id = int(fields[0])
                    self.director_dict[douban_id] = []
                    self.actor_dict[douban_id] = []
                    diretors = fields[1].split('$$')
                    actors = fields[2].split('$$')
                    for director in diretors:
                        name_parts = self.saperate_name(director)
                        for name_part in name_parts:
                            self.director_dict[douban_id].append(name_part)
                    for actor in actors:
                        name_parts = self.saperate_name(actor)
                        for name_part in name_parts:
                            self.actor_dict[douban_id].append(name_part)
                except Exception, e:
                    pass


    def entity_recgonize(self, douban_id, sentence):
        sentence_entity = None
        txt = self.recompose_sentence(sentence)
        for entity, keywords in entity_dict.items():
            for keyword in keywords:
                if keyword in txt:
                    sentence_entity = (entity, 'general')

        for name in self.director_dict[douban_id]:
            if name in txt:
                sentence_entity = (name, 'director')
        for name in self.actor_dict[douban_id]:
            if name in txt:
                sentence_entity = (name, 'actor')
        # if sentence_entity is None:
        #     sentence_entity = (u'影片整体质量', 'general')
        return sentence_entity



    def classify_string(self, txt):
        seg_result = Tokenize.tokenize_string(txt, 'unicode')
        sentences = self.get_sentences(seg_result)
        for sentence in sentences:
            opinion = self.classify_sentence(sentence)
            tokens = map(lambda x: x[0].encode('utf8') + x[1], sentence)
            #print ' '.join(tokens) + ' | ' + str(opinion)


    def get_sentences(self, seg_result):
        sentences = []
        start = 0
        end = 0
        words = seg_result['ret']
        while end < len(words):
            sentence, end = self.get_first_sentence(words, start)
            if len(Feature.get_verb_noun(sentence)) > 0:
                sentences.append(sentence)
            start = end
        return sentences


    def get_first_sentence(self, words, start):
        sentence = []
        none_w_start = start
        while none_w_start < len(words) and \
                words[none_w_start][1] is 'w':
            none_w_start += 1
        end = none_w_start
        while end < len(words) and \
                words[end][1] is not 'w':
            sentence.append(words[end])
            end += 1
        return sentence, end



    def classify_sentence(self, words):
        valid_token_set = Feature.get_verb_noun(words)
        p_positive = 1
        p_negtive = 1
        print 'sentence: %s' % self.recompose_sentence(words).encode('utf8')
        for token in valid_token_set:
            p_token_positive = self.positivie_token_dict.get(token, \
                    1/float(self.positive_cnt + 2))
            p_token_negtive = self.negtive_token_dict.get(token, \
                    1/float(self.negtive_cnt + 2))
            print 'token: %s: %s\t%s' % (token.encode('utf8'), p_token_positive, \
                    p_token_negtive)
            p_positive *= p_token_positive
            p_negtive *= p_token_negtive

        epsilon = 0.1
        p_positive = p_positive/(p_positive + p_negtive)
        print 'p_positive: %s' % p_positive
        if p_positive > 0.5 + epsilon:
            return 1
        elif p_positive < 0.5 - epsilon:
            return -1
        else:
            return 0

    def recompose_sentence(self, words):
        tokens = map(lambda x: x[0], words)
        txt = ''.join(tokens)
        return txt
        


    def summarize_sentence(self, words, douban_id):
        #summarizations = []
        output_str = None
        entity = self.entity_recgonize(douban_id, words)
        opinion = self.classify_sentence(words)
        if entity is not None and opinion is not 0:
            #print '%s\t%s' % (entity[0].encode('utf8'), opinion)
            output_str = entity[0] + junction_dict[entity[1]] + \
                    opinion_dict[opinion]
        # elif entity is not None:
        #     output_str = entity[0]
        return output_str
        #return summarizations

    def summarize_string(self, txt, douban_id):
        seg_result = Tokenize.tokenize_string(txt, 'unicode')
        sentences = self.get_sentences(seg_result)
        #print sentences
        summarizations = []
        for sentence in sentences:
            summarization = self.summarize_sentence(sentence, douban_id)
            if summarization is not None:
                print 'summarization: %s' % summarization.encode('utf8')
                summarizations.append(summarization)
        return summarizations

    def summarize_comments(self, douban_id):
        comments = DoubanComment.get_comments(douban_id)
        for comment in comments:
            print 'comment: %s' % comment['comment'].encode('utf8')
            self.summarize_string(comment['comment'], douban_id)


if __name__=='__main__':
    #test_str = '这真是一部烂片'
    #test_str = '这部电影真精彩, 这是一部经典的烂片'.decode('utf8')
    test_str = '吴镇宇的感觉很不错，陈冠希在片尾的表情超级帅。'.decode('utf8')
    douban_id = 1307106
    classifier = Classify()
    #classifier.summarize_string(test_str, douban_id)
    classifier.summarize_comments(1307106)
    #classifier.classify_string(test_str)



