import os
import sys
sys.path.append('..')
from Config import Config

class Movie:
    def __init__(self):
        self.id_map_dict = {}
        self.movie_title_dict = {}
        self.movies = set()
        self.load_id_map()
        self.load_movie_title()

    def load_id_map(self):
        id_map_obj = open(os.path.join(Config.db_file_path, 'id_map'))
        with id_map_obj:
            for line in id_map_obj:
                try:
                    fields = line.strip().split('\t')
                    douban_id = fields[1]
                    works_id = fields[0]
                    self.id_map_dict[douban_id] = works_id
                except Exception, e:
                    pass

    def load_movie_title(self):
        movie_obj = open(os.path.join(Config.db_file_path, 'movie'))
        with movie_obj:
            for line in movie_obj:
                try:
                    fields = line.strip().split('\t')
                    works_id = fields[0]
                    title = fields[1].decode('utf8')
                    self.movie_title_dict[works_id] = title
                except Exception, e:
                    print e

    def load_douban_ids(self, comment_cnt_lower_bound):
        douban_ids = os.listdir(Config.short_comment_path)
        for douban_id in douban_ids:
            input_path = os.path.join(Config.short_comment_path, douban_id)
            input_obj = open(input_path)
            with input_obj:
                line_cnt = len(input_obj.readlines())
            if line_cnt >= comment_cnt_lower_bound:
                self.movies.add(douban_id)
        return self.movies


    def get_title(self, douban_id):
        works_id = self.id_map_dict.get(douban_id, -1)
        print works_id
        title = self.movie_title_dict.get(works_id, None)
        return title

if __name__=='__main__':
    movie_op = Movie()
    print 'movie_title_dict length %s' % len(movie_op.movie_title_dict)
    print movie_op.get_title('1304447').encode('utf8')
