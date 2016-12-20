import os
import sys
sys.path.append('..')
from Feature import Feature
from Config import Config
from Genome import Genome
import math

class Tagging:
    def __init__(self):
        pass

    @staticmethod
    def tf_2_tfidf(tf_dict):
        idf_dict = Feature.get_idf_dict()
        if len(tf_dict) > 0:
            tf_idf_list = map(lambda x: (x[0], idf_dict[x[0]]*x[1]), \
                    tf_dict.items())
            sorted_list = sorted(tf_idf_list, key=lambda x: -x[1])
            return dict(sorted_list[:100])
        else:
            return {}

    @staticmethod
    def norm_cal(tf_idf_dict):
        squares = map(lambda x: x[1]*x[1], tf_idf_dict.items())
        norm = math.sqrt(reduce(lambda a, b: a+b, squares))
        return norm


    @staticmethod
    def cos_sim(tf_idf_dicts):
        common_terms = set(tf_idf_dicts[0]).\
                intersection(set(tf_idf_dicts[1]))
        if len(common_terms) == 0:
            return 0
        else:
            result = 0
            for term in common_terms:
                result += tf_idf_dicts[0][term] * tf_idf_dicts[1][term]

            result = result/(Tagging.norm_cal(tf_idf_dicts[0]) * \
                    Tagging.norm_cal(tf_idf_dicts[1]))
            return result

    @staticmethod
    def movie_genome_sim(douban_id, genome_id, movie_tf_idf_path, \
            genome_tf_idf_path):
        movie_tf_idf_dict = dict(Feature.get_tf_idf_from_file(douban_id, \
                movie_tf_idf_path))
        genome_tf_idf_dict = dict(Genome.get_tf_idf_from_file(genome_id, \
                genome_tf_idf_path))

        return Tagging.cos_sim([movie_tf_idf_dict, genome_tf_idf_dict])

    @staticmethod
    def get_genome_sim_list(douban_id, movie_tf_idf_path, genome_tf_idf_path, \
            genome_num=10):
        sim_dict = {}
        genome_dict = Genome.load_genome_dict()
        for genome_id in genome_dict:
            sim = Tagging.movie_genome_sim(douban_id, genome_id, \
                    movie_tf_idf_path, genome_tf_idf_path)
            sim_dict[genome_id] = sim
        genome_list = sorted(sim_dict.items(), key=lambda x: -x[1])
        # genome_name_list = map(lambda x: (x[0], genome_dict[x[0]]['name'], \
        #         x[1]), genome_list)
        # return genome_name_list[:genome_num]
        return genome_list



if __name__=='__main__':
    tagging = Tagging()
    #sim_list = tagging.get_genome_sim_list('1652587', 20)
    sim_list = tagging.get_genome_sim_list('1652587', \
            Config.train_tf_idf_path, Config.train_genome_tf_idf_path, 20)
    for genome_id, name, sim in sim_list:
        print '%s\t%s\t%s' % (genome_id, name.encode('utf8'), sim)



