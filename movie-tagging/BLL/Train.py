import sys
sys.path.append('..')
import random
from Movie import Movie
from Config import Config
from Feature import Feature
from Genome import Genome


class Train:
    def __init__(self):
        pass

    @staticmethod
    def simple_partition(comment_cnt_lower_bound, train_ratio):
        movie_op = Movie()
        uni_set = movie_op.load_douban_ids(comment_cnt_lower_bound)
        print 'total movie cnt %s' % len(uni_set)
        train_set = set(random.sample(uni_set, int(len(uni_set)*train_ratio)))
        cv_set = uni_set - train_set
        train_obj = open(Config.train_set_path, 'w')
        with train_obj:
            for douban_id in train_set:
                train_obj.write('%s\n' % douban_id)
        cv_obj = open(Config.cv_set_path, 'w')
        with cv_obj:
            for douban_id in cv_set:
                cv_obj.write('%s\n' % douban_id)

        return (train_set, cv_set)

    @staticmethod
    def tf_idf_training(comment_cnt_lower_bound, train_ratio):
        # train_set, cv_set = Train.simple_partition(comment_cnt_lower_bound, \
        #         train_ratio)
        # idf_dict = Feature.cal_idf(train_set, Config.train_idf_path)
        train_set = Train.get_train_set()
        Feature.cal_tf_idf(train_set, Config.train_idf_path, Config.train_tf_idf_path, True, 200)
        Genome.cal_tf_idf(Config.train_tf_idf_path, \
                Config.train_genome_tf_idf_path, 200)

    @staticmethod
    def get_train_set():
        train_set = set()
        input_obj = open(Config.train_set_path)
        with input_obj:
            for line in input_obj:
                douban_id = line.strip()
                train_set.add(douban_id)
        return train_set


if __name__=='__main__':
    Train.tf_idf_training(50, 0.7)


