import os
import sys
sys.path.append('..')
from Tokenizer import Tokenizer
from Config import Config
from DAL.DoubanComment import DoubanComment
import math

MAX_FEATURE_NUM = 1000

class Feature:
    def __init__(self):
        pass

    @staticmethod
    def load_stop_words():
        stop_words = set()
        input_obj = open(Config.stop_word_path)
        with input_obj:
            for line in input_obj:
                stop_word = line.strip().decode('utf8')
                stop_words.add(stop_word)
        return stop_words

    @staticmethod
    def get_tf(douban_id, tokenizer, feature_num=MAX_FEATURE_NUM):
        tf = dict()
        input_obj = open(os.path.join(Config.short_comment_path, \
                str(douban_id)))
        comments = DoubanComment.get_comments(douban_id)
        for comment in comments:
            valid_tokens_set = Feature.get_valid_tokens(comment['comment'], tokenizer)
            for token in valid_tokens_set:
                tf[token] = tf.get(token, 0) + 1
        tf_list = sorted(tf.iteritems(), key=lambda x: x[1], \
                reverse=True)[:feature_num]
        return tf_list

    @staticmethod
    def get_tf_from_file(douban_id):
        stop_words = Feature.load_stop_words()
        tf_dict = {}
        tf_path = os.path.join(Config.tf_path, douban_id)
        if not os.path.exists(tf_path):
            return {}
        else:
            input_obj = open(tf_path)
            with input_obj:
                for line in input_obj:
                    fields = line.strip().split('\t')
                    try:
                        term = fields[0].decode('utf8')
                        if not term in stop_words:
                            freq = int(fields[1])
                            tf_dict[term] = freq
                    except Exception, e:
                        pass
            return tf_dict

    @staticmethod
    def get_idf_from_file(idf_path):
        idf_dict = {}
        input_obj = open(Config.idf_path)
        with input_obj:
            for line in input_obj:
                fields = line.strip().split('\t')
                try:
                    term = fields[0].decode('utf8')
                    idf = float(fields[1])
                    idf_dict[term] = idf
                except Exception, e:
                    pass
        return idf_dict


    # --------------------------------------------------------------------------
    ##
    # @Synopsis  return [(term, tf_idf)] sorted by tf_idf desc
    # ----------------------------------------------------------------------------
    @staticmethod
    def get_tf_idf(douban_id, idf_dict, feature_num=MAX_FEATURE_NUM):
        tf_dict = Feature.get_tf_from_file(douban_id)
        tf_idf_dict = {}
        for term, feq in tf_dict.items():
            idf = idf_dict.get(term, None)
            if idf is not None:
                tf_idf = feq * idf
                tf_idf_dict[term] = tf_idf
        sorted_features = sorted(tf_idf_dict.items(), key=lambda x:-x[1])\
                [:feature_num]
        return sorted_features

    @staticmethod
    def get_tf_idf_from_file(douban_id, movie_tf_idf_path):
        tf_idf_list = []
        input_path = os.path.join(movie_tf_idf_path, douban_id)
        if os.path.exists(input_path):
            input_obj = open(input_path)
            with input_obj:
                for line in input_obj:
                    fields = line.strip().split('\t')
                    try:
                        term = fields[0].decode('utf8')
                        tf_idf = float(fields[1])
                        tf_idf_list.append((term, tf_idf))
                    except Exception, e:
                        pass
        return tf_idf_list

    @staticmethod
    # --------------------------------------------------------------------------
    ##
    # @Synopsis  Calculate all movie tf_idf and store them into output_path
    #
    # @Param movie_set The set of movie to be calculated, meaning idf is for
    # this set
    # @Param idf_path
    # @Param output_path
    # @Param normalize Whether to normalize all movies' tf_idf vector
    # @Param feature_num
    #
    # @Returns
    # ----------------------------------------------------------------------------
    def cal_tf_idf(movie_set, idf_path, output_path, normalize=False, feature_num = 100):
        processed_id_cnt = 0
        idf_dict = Feature.get_idf_from_file(idf_path)
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        for douban_id in movie_set:
            print 'processing %s' % douban_id
            tf_idf_list = Feature.get_tf_idf(douban_id, idf_dict)[:feature_num]
            if normalize:
                values = map(lambda x: x[1], tf_idf_list)
                square_values = map(lambda x: x*x, values)
                norm = math.sqrt(sum(square_values))

                tf_idf_list = map(lambda x: (x[0], x[1]/norm), \
                        tf_idf_list)
            output_obj = open(os.path.join(output_path, \
                    douban_id), 'w')
            with output_obj:
                for term, tf_idf in tf_idf_list:
                    output_obj.write('%s\t%s\n' % (term.encode('utf8'), \
                        tf_idf))
            processed_id_cnt += 1
            print '%s movie processed' % processed_id_cnt


    @staticmethod
    def get_valid_tokens(txt, tokenizer):
        seg_result = tokenizer.tokenize_string(txt, 'unicode')
        valid_token_set = Feature.get_verb_noun(seg_result['ret'])
        return valid_token_set

    @staticmethod
    def get_verb_noun(words):
        valid_words = filter(lambda x: x[1] in ['a', 'n', 'Ng', 'Ag', 'an', \
                'i', 'j', 'nr', 'ns', 'nt', 'nx', 'Vg', 'v', 'vd', 'vn'], \
                words)
        valid_tokens = map(lambda x: x[0], valid_words)
        valid_token_set = set(valid_tokens)
        return valid_token_set



    @staticmethod
    def get_all_tf(feature_num=MAX_FEATURE_NUM):
        processed_id_cnt = 0
        tf = dict()
        tokenizer = Tokenizer()
        for root, dirs, files in os.walk(Config.short_comment_path):
            for file_name in files:
                douban_id = file_name
                print 'processing %s' % douban_id
                tf_list = Feature.get_tf(douban_id, tokenizer, feature_num)
                processed_id_cnt += 1
                print '%s movie processed' % processed_id_cnt
                output_obj = open(os.path.join(Config.tf_path, \
                        douban_id), 'w')
                with output_obj:
                    for term, frequency in tf_list:
                        output_obj.write('%s\t%s\n' % (term.encode('utf8'), \
                            frequency))

    @staticmethod
    def cal_idf(movie_set, output_path):
        df_dict = {}
        for douban_id in movie_set:
            input_obj = open(os.path.join(Config.tf_path, \
                    douban_id))
            term_dict = {}
            with input_obj:
                for line in input_obj:
                    try:
                        term = line.strip().split('\t')[0]
                        #df_dict[term] = df_dict.get(term, 0) + 1
                        term_dict[term] = 1
                    except Exception, e:
                        pass
            for term in term_dict:
                df_dict[term] = df_dict.get(term, 0) + 1
        movie_cnt = len(movie_set)
        print 'movie_cnt: %s' % movie_cnt
        df_list = sorted(df_dict.items(), key=lambda x:x[1])
        df_list = filter(lambda x: x[1] > 1, df_list)
        idf_list = map(lambda x: (x[0], math.log(movie_cnt/float(x[1]))), \
                df_list)
        output_obj = open(output_path, 'w')
        with output_obj:
            for term, idf in idf_list:
                output_obj.write('%s\t%s\n' % (term, idf))
        return dict(idf_list)


if __name__ == '__main__':
    #Feature.get_all_tf()
    #Feature.get_tf(1304447)
    #Feature.get_idf()
    #Feature.get_all_tf_idf()
    features = Feature.get_tf_idf_from_file('1304447', Config.tf_idf_path)
    print features
