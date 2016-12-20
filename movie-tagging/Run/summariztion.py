#-*- encoding: utf-8 -*-

import sys
sys.path.append('..')
import json
# import wordseg, postag
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
# from BLL.Feature import Feature
from DAL.DoubanComment import DoubanComment
from BLL.Classify import Classify

class ApiHTTPHandle(BaseHTTPRequestHandler):
    def procDoubanId(self, uri):
        douban_id = uri[len('/api?id='):]
        douban_id = int(douban_id)
        comments = DoubanComment.get_comments(douban_id)
        classifier = Classify()
        summarized_comments = []
        summarization_dict = {}
        for comment in comments:
            summarizations = classifier.summarize_string(comment['comment'], douban_id)
            if summarizations is not None:
                for summarization in summarizations:
                    summarization_dict[summarization] = \
                            summarization_dict.get(summarization, 0) + 1
                #print 'summarizations: %s' % len(summarizations)
                summarized_comments.append('(' + ','.join(summarizations) + \
                        ') ' + comment['comment'])
            else:
                summarized_comments.append(comment['comment'])
        sorted_summariztions = sorted(summarization_dict.items(), \
                key=lambda x: -x[1])
        summarizations_str = ','.join(['%s:%s' % (x[0], x[1]) for x in \
                sorted_summariztions])
        return 200, {'error': 'succ', 'doubanId': douban_id, \
                'summarizations': summarizations_str, 'comments': \
                summarized_comments}

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
