import sys
sys.path.append('..')
from Feature import Feature
from DAL.DoubanComment import DoubanComment
from Config import Config
import os

class Training:
    def __init__(self):
        pass

    @staticmethod
    def get_rating_distribution():
        rating_dict = {}
        for root, dirs, files in os.walk(Config.short_comment_path):
            for file_name in files:
                input_obj = open(os.path.join(root, file_name))
                with input_obj:
                    for line in input_obj:
                        fields = line.strip().split('\t')
                        try:
                            rating = int(fields[1])
                            rating_dict[rating] = rating_dict.get(rating, 0)\
                                    + 1
                        except Exception, e:
                            print Exception
        output_obj = open(Config.derivants_data_path + '/rating_distribution'\
                , 'w')
        with output_obj:
            for rating, cnt in rating_dict.items():
                output_obj.write('%s\t%s\n' % (rating, cnt))


    @staticmethod
    def train_opinion_tokens():
        comment_cnt_dict = {}
        token_df_dicts = {}
        processed_file_cnt = 0
        for root, dir, files in os.walk(Config.short_comment_path):
            for file_name in files:
                douban_id = file_name
                comments = DoubanComment.get_comments(douban_id)
                for comment in comments:
                    rating = comment['rating']
                    if rating == 50 or rating == 10:
                        comment_cnt_dict[rating] = \
                                comment_cnt_dict.get(rating, 0) + 1
                        token_df_dicts[rating] = token_df_dicts.get(rating, {})
                        valid_tokens_set = Feature.get_valid_tokens(\
                                comment['comment'])
                        for token in valid_tokens_set:
                            token_df_dicts[rating][token] = \
                                    token_df_dicts[rating].get(token, 0) + 1
                processed_file_cnt += 1
                print 'processed %s files' % processed_file_cnt
                # if processed_file_cnt >= 1000:
                #     break
        for rating, comment_cnt in comment_cnt_dict.items():
            token_df_dict = token_df_dicts[rating]
            token_df_list = sorted(token_df_dict.items(), key=lambda x:-x[1])
            output_obj = open(os.path.join(Config.opinion_path, \
                    str(rating)), 'w')
            output_obj.write('%s\n' % comment_cnt)
            for token, df in token_df_list:
                output_obj.write('%s\t%s\n' % (token.encode('utf8'), df))




if __name__=='__main__':
    #Training.get_rating_distribution()
    Training.train_opinion_tokens()
