import sys
import os
sys.path.append('..')
from BLL.Tagging import Tagging
from BLL.Genome import Genome
from Config import Config
from BLL.Feature import Feature

class CrossValidation:
    def __init__(self):
        pass

    @staticmethod
    def get_cv_set():
        cv_set = set()
        input_obj = open(Config.cv_set_path)
        with input_obj:
            for line in input_obj:
                douban_id = line.strip()
                cv_set.add(douban_id)
        return cv_set


    @staticmethod
    def get_prediction(cv_set, output_path):
        cv_set = CrossValidation.get_cv_set()
        total_cnt = len(cv_set)
        processed_cnt = 0
        idf_dict = Feature.cal_idf(cv_set, Config.cv_idf_path)
        Feature.cal_tf_idf(cv_set, Config.cv_idf_path, Config.cv_tf_idf_path, 200)
        genome_dict = Genome.load_genome_dict()
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        for douban_id in cv_set:
            genome_predict = Tagging.get_genome_sim_list(douban_id, \
                    Config.cv_tf_idf_path, Config.train_genome_tf_idf_path, 20)
            output_obj = open(os.path.join(output_path, \
                    douban_id), 'w')
            with output_obj:
                for genome_id, sim in genome_predict:
                    genome_name = genome_dict[genome_id]['name'].encode('utf8')
                    output_obj.write('\t'.join([genome_id, genome_name, \
                            str(sim)]) + '\n')
            processed_cnt += 1
            print '%s/%s movie processed' % (processed_cnt, total_cnt)

    @staticmethod
    def evaluation(prediction_path):
        cv_set = CrossValidation.get_cv_set()
        movie_genome_set_dict = Genome.load_movie_genome_dict()
        predict_dict = {}
        for douban_id in cv_set:
            genome_list = []
            input_path = os.path.join(Config.tf_idf_prediction_path, douban_id)
            input_obj = open(input_path)
            with input_obj:
                for line in input_obj:
                    fields = line.strip().split('\t')
                    genome_id = fields[0]
                    genome_name = fields[1].decode('utf8')
                    sim = float(fields[2])
                    genome_list.append((genome_id, sim))
            predict_dict[douban_id] = genome_list

        # precision_recall_dict = {}
        # for truncate in xrange(1, 101):
        #     truth_size = 0
        #     prediction_size = 0
        #     intersection_size = 0

        #     for douban_id in cv_set:
        #         truth_set = movie_genome_set_dict.get(douban_id, set())
        #         predict_list = predict_dict[douban_id][:truncate]
        #         predict_set = set(map(lambda x: x[0], predict_list))
        #         truth_size += len(truth_set)
        #         prediction_size += len(predict_set)
        #         intersection_size += len(predict_set.intersection(truth_set))
        #     precision = intersection_size/float(prediction_size)
        #     recall = intersection_size/float(truth_size)
        #     precision_recall_dict[truncate] = (precision, recall)
        #     print '%s\t%s\t%s' % (truncate, precision, recall)

        # output_obj = open(os.path.join(Config.cv_path, 'evaluation_regulated.txt'), 'w')
        # with output_obj:
        #     for truncate, performance in sorted(precision_recall_dict.items()):
        #         precision, recall = performance
        #         output_obj.write('%s\t%s\t%s\n' % (truncate, precision, recall))
        
        precision_recall_dict = {}
        th_list = map(lambda x: float(x)/100, range(1,100))
        for th in th_list:
            truth_size = 0
            prediction_size = 0
            intersection_size = 0

            for douban_id in cv_set:
                truth_set = movie_genome_set_dict.get(douban_id, set())
                predict_list = filter(lambda x: x[1]>=th, predict_dict[douban_id])
                predict_set = set(map(lambda x: x[0], predict_list))
                truth_size += len(truth_set)
                prediction_size += len(predict_set)
                intersection_size += len(predict_set.intersection(truth_set))
            if not prediction_size == 0:
                precision = intersection_size/float(prediction_size)
                recall = intersection_size/float(truth_size)
                precision_recall_dict[th] = (precision, recall)
                print '%s\t%s\t%s' % (th, precision, recall)
            else:
                break

        output_obj = open(os.path.join(Config.cv_path, 'evaluation_normaized_th_200features.txt'), 'w')
        with output_obj:
            for th, performance in sorted(precision_recall_dict.items()):
                precision, recall = performance
                output_obj.write('%s\t%s\t%s\n' % (th, precision, recall))





if __name__=='__main__':
    cv_set = CrossValidation.get_cv_set()
    CrossValidation.get_prediction(cv_set, Config.tf_idf_prediction_path)
    CrossValidation.evaluation(Config.tf_idf_prediction_path)


