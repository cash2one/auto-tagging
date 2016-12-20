import sys
sys.path.append('..')
import os
from Feature import Feature
from Config import Config
import math

MAX_FEATURE_NUM = 2000
class Genome:
    def __init__(self):
        pass

    @staticmethod
    def load_genome_dict():
        genome_dict = {}
        input_obj = open(Config.genome_path)
        used_genome_obj = open(Config.used_genome_path)
        used_genomes = set()
        with used_genome_obj:
            for line in used_genome_obj:
                used_genomes.add(line.strip())

        with input_obj:
            for line in input_obj:
                fields = line.strip().split('\t')
                try:
                    genome_id = fields[0]
                    if genome_id in used_genomes:
                        name_chs = fields[1].decode('utf8', 'ignore')
                        name_eng = fields[2]
                        level = fields[3]
                        father_id = fields[4]
                        genome_dict[genome_id] = \
                                {'name': name_chs, 'father_id': father_id}
                except Exception, e:
                    pass
        return genome_dict

    @staticmethod
    def load_movie_genome_dict():
        movie_genome_dict = {}
        input_obj = open(Config.genome_movie_path)
        id_map_obj = open(Config.id_map_path)
        id_map_dict = {}
        with id_map_obj:
            for line in id_map_obj:
                fields = line.strip().split('\t')
                try:
                    works_id = fields[0]
                    douban_id = fields[1]
                    id_map_dict[works_id] = douban_id
                except Exception, e:
                    pass

        with input_obj:
            for line in input_obj:
                fields = line.strip().split('\t')
                try:
                    genome_id = fields[0]
                    works_id = fields[2]
                    genome_score = int(fields[3])
                    douban_id = id_map_dict[works_id]
                    if genome_score >= 2:
                        movie_genome_dict[douban_id] = movie_genome_dict\
                                .get(douban_id, set())
                        movie_genome_dict[douban_id].add(genome_id)
                except Exception, e:
                    pass
                    # print Exception
                    # print e
        return movie_genome_dict



    @staticmethod
    def load_genome_movie():
        genome_movie_dict = {}
        input_obj = open(Config.genome_movie_path)
        id_map_obj = open(Config.id_map_path)
        id_map_dict = {}
        with id_map_obj:
            for line in id_map_obj:
                fields = line.strip().split('\t')
                try:
                    works_id = fields[0]
                    douban_id = fields[1]
                    id_map_dict[works_id] = douban_id
                except Exception, e:
                    pass

        with input_obj:
            for line in input_obj:
                fields = line.strip().split('\t')
                try:
                    genome_id = fields[0]
                    works_id = fields[2]
                    genome_score = int(fields[3])
                    douban_id = id_map_dict[works_id]
                    if genome_score >= 2:
                        genome_movie_dict[genome_id] = \
                                genome_movie_dict\
                                .get(genome_id, set())
                        genome_movie_dict[genome_id].add(douban_id)
                except Exception, e:
                    pass
        return genome_movie_dict


    @staticmethod
    def cal_tf(genome_id):
        genome_movie_dict = Genome.load_genome_movie()
        movie_set = genome_movie_dict.get(genome_id, set())
        #print '%s have %s movies' % (genome_id, len(movie_set))
        genome_tf_dict = {}
        for douban_id in movie_set:
            movie_tf_dict = Feature.get_tf_from_file(douban_id)
            #print '%s have %s terms' % (douban_id, len(movie_tf_dict))
            for term, freq in movie_tf_dict.items():
                genome_tf_dict[term] = genome_tf_dict.get(term, 0) + freq
        return genome_tf_dict


    @staticmethod
    def get_tf_from_file(genome_id):
        tf_dict = {}
        stop_words = Feature.load_stop_words()
        input_file = os.path.join(Config.genome_tf_path, genome_id)
        if os.path.exists(input_file):
            input_obj = open(input_file)
            with input_obj:
                for line in input_obj:
                    fields = line.strip().split('\t')
                    try:
                        term = fields[0].decode('utf8')
                        if not term in stop_words:
                            tf = int(fields[1])
                            tf_dict[term] = tf
                    except Exception, e:
                        pass
        return tf_dict

    @staticmethod
    def cal_all_tf(feature_num=MAX_FEATURE_NUM):
        genome_dict = Genome.load_genome_dict()
        processed_genome_cnt = 0
        for genome_id in genome_dict:
            print 'processing %s' % genome_dict[genome_id]['name'].\
                    encode('utf8')
            tf_dict = Genome.cal_tf(genome_id)
            output_obj = open(os.path.join(Config.genome_tf_path, \
                    str(genome_id)), 'w')
            with output_obj:
                for term, feq in sorted(tf_dict.items(), key=lambda x: -x[1]):
                    output_obj.write('%s\t%s\n' % (term.encode('utf8'), \
                            feq))
            processed_genome_cnt += 1
            print 'processed %s genomes' % processed_genome_cnt


    @staticmethod
    def get_tf_idf(genome_id, movie_tf_idf_path, feature_num=100):
        genome_movie_dict = Genome.load_genome_movie()
        processed_genome_cnt = 0
        genome_tf_idf_dict = {}
        movie_set = genome_movie_dict.get(genome_id, set())
        for douban_id in movie_set:
            tf_idf_dict = dict(Feature.get_tf_idf_from_file(douban_id, movie_tf_idf_path))
            for term, tf_idf in tf_idf_dict.items():
                genome_tf_idf_dict[term] = genome_tf_idf_dict\
                        .get(term, 0) + tf_idf
        sorted_features = sorted(genome_tf_idf_dict.items(), key=lambda x:-x[1])\
                [:feature_num]
        return sorted_features

    @staticmethod
    def get_tf_idf_from_file(genome_id, genome_tf_idf_path):
        genome_tf_idf_list = []
        input_path = os.path.join(genome_tf_idf_path, genome_id)
        if os.path.exists(input_path):
            input_obj = open(input_path)
            with input_obj:
                for line in input_obj:
                    fields = line.strip().split('\t')
                    term = fields[0].decode('utf8')
                    tf_idf = float(fields[1])
                    genome_tf_idf_list.append((term, tf_idf))
        return genome_tf_idf_list

    @staticmethod
    def cal_tf_idf(movie_tf_idf_path, output_path, feature_num=100):
        genome_dict = Genome.load_genome_dict()
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        for genome_id in genome_dict:
            print 'processing genome %s: %s' % (genome_id, \
                genome_dict[genome_id]['name'].encode('utf8'))
            sorted_features = Genome.get_tf_idf(genome_id, movie_tf_idf_path, feature_num)
            output_obj = open(os.path.join(output_path, genome_id), 'w')
            with output_obj:
                for term, tf_idf in sorted_features:
                    output_obj.write('%s\t%s\n' % \
                            (term.encode('utf8'), tf_idf))

if __name__=='__main__':
    #Genome.get_all_tf_idf()
    print Genome.get_tf_idf_from_file('36', Config.genome_tf_idf_path)
    #Genome.load_movie_genome_dict()

