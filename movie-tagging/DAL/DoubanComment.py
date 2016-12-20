import sys
import os
sys.path.append('..')
from Config import Config

class DoubanComment:
    def __init__(self):
        pass

    @staticmethod
    # --------------------------------------------------------------------------
    ##
    # @Synopsis  get comment of a movie from file
    #
    # @Param douban_id
    #
    # @Returns  [{'votes':, 'rating':, 'comment':}]
    # ----------------------------------------------------------------------------
    def get_comments(douban_id):
        input_obj = open(os.path.join(Config.short_comment_path, \
            str(douban_id)))
        with input_obj:
            # comments = [line.decode('gbk').split('\t')[2].strip() \
            #         for line in input_obj]
            comments_list = []
            for line in input_obj:
                fields = line.strip('\n').split('\t')
                try:
                    votes = int(fields[0])
                    rating = int(fields[1])
                    comment = fields[2].decode('utf8')
                    comment_dict = {}
                    comment_dict['votes'] = votes
                    comment_dict['rating'] = rating
                    comment_dict['comment'] = comment
                    comments_list.append(comment_dict)
                except Exception:
                    print Exception

        return comments_list

