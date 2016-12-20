#-*- encoding: utf-8 -*-

import sys
sys.path.append('..')
import json
import wordseg, postag
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from BLL.Feature import Feature
from BLL.Tagging import Tagging
from BLL.Movie import Movie
from BLL.Genome import Genome
from DAL.DoubanComment import DoubanComment

class ApiHTTPHandle(BaseHTTPRequestHandler):
    def procDoubanId(self, uri):
        douban_id = uri[len('/api?id='):]
        # comments = DoubanComment.get_comments(douban_id)
        # comments = map(lambda x:x['comment'], comments)
        movie_genome_dict = Genome.load_movie_genome_dict()
        genome_dict = Genome.load_genome_dict()

        genomes = movie_genome_dict.get(douban_id, set())
        genome_str = ' '.join([genome_dict[genome_id]['name'] for genome_id \
                in genomes])
        
        feature = Feature.get_tf_idf_from_file(douban_id)
        feature_str = ' '.join(['%s:%s' %(k, v) for k, v in feature])
        sim_genome = Tagging.get_genome_sim_list(douban_id, 20)
        sim_genome_str = ' '.join(['%s:%s' % (name, sim) for \
                (genome_id, name, sim) in sim_genome])
        sim_genome_features = []
        for genome_id, name, sim in sim_genome:
            genome_tf_idf_list = Genome.get_tf_idf_from_file(genome_id)
            genome_feature_str = ' '.join(['%s:%s' % (k, v) for k, v in \
                    genome_tf_idf_list])
            sim_genome_features.append((name, genome_feature_str))


        movie_op = Movie()
        title = movie_op.get_title(douban_id)
        return 200, {'error': 'succ', 'doubanId': douban_id, 'title': title,\
                'genomes': genome_str,
                'feature': feature_str, 'extend_genomes': sim_genome_str, \
                'genome_feature': sim_genome_features}

    def do_GET(self):
        method, uri, protocol = self.raw_requestline.strip('\r\n').split(' ')
        if uri.find('/api?id=') == 0:
            code, result = self.procDoubanId(uri)
        else:
            code, result = 404, {'error': 'unrecognized uri'}
        self.protocal_version = 'HTTP/1.1'
        self.send_response(code)
        self.end_headers()
        self.wfile.write(json.dumps(result))

if __name__ == '__main__':
    http_server = HTTPServer(('', int(sys.argv[1])), ApiHTTPHandle)
    http_server.serve_forever()
