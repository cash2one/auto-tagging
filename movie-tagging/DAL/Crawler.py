#-*- encoding: utf-8 -*-
import sys
sys.path.append('..')

import os
from DAL.HtmlParser import HtmlParser
from Config import Config
from time import sleep
from functools import wraps
import urllib2, logging
import threading
import datetime


class Crawler:
    mutex = threading.Lock()
    douban_id_cnt = 0
    fetched_id_cnt = 0
    crawled_douban_ids = []
    comment_num_dict = {}
    start_time = datetime.datetime.now()
    def __init__(self):
        logging.basicConfig()
        self.log = logging.getLogger('retry')

    def retry(f):
        @wraps(f)
        def wrapped_f(self, *args, **kwargs):
            MAX_ATTEMPTS = 5
            for attempt in xrange(1, MAX_ATTEMPTS + 1):
                try:
                    return f(self, *args, **kwargs)
                except Exception as ex:
                    self.log.exception('Attempt %s/%s failed[%s]: %s', \
                            attempt, MAX_ATTEMPTS, ex, (args, kwargs))
                    sleep(1 * attempt)
            self.log.critical('All %s atempts failed: %s', MAX_ATTEMPTS, \
                    (args, kwargs))
        return wrapped_f

    @retry
    def fetch_content(self, url):
        r = urllib2.Request(url)
        f = urllib2.urlopen(r, data = None, timeout = 3)
        return f.read()


    def multi_thread_crawl(self, thread_num, content_type):
        douban_ids = []
        id_map_obj = open(Config.id_map_path)
        with id_map_obj:
            for line in id_map_obj:
                try:
                    douban_id = line.strip().split('\t')[1]
                    douban_ids.append(douban_id)
                except Exception, e:
                    pass
        #douban_ids = douban_ids[:2]
        id_cnt = len(douban_ids)
        self.douban_id_cnt = len(douban_ids)
        id_cnt_per_thread = id_cnt/thread_num
        threads = []
        for i in xrange(0, thread_num):
            id_fraction = douban_ids[i:][::thread_num]
            t = threading.Thread(target = self.fetch_comments_multiple_ids,\
                    args = (id_fraction, ))

            threads.append(t)

        self.start_time = datetime.datetime.now()
        for t in threads:
            t.start()


    def fetch_comments_multiple_ids(self, ids):
        for id in ids:
            self.fetch_comments(id)
            if self.mutex.acquire(1):
                self.fetched_id_cnt += 1
                self.crawled_douban_ids.append(id)
                curr_time = datetime.datetime.now()
                time_passed = (curr_time - self.start_time).seconds
                print ('fetched %s/%s ids, %s seconds passed, expect to finish'
                    ' in %s hours') % (self.fetched_id_cnt, self.douban_id_cnt,\
                    time_passed, float(time_passed)*self.douban_id_cnt/\
                    self.fetched_id_cnt/3600)

                self.mutex.release()
        output_obj = open(Config.short_comment_path + 'comment_cnt.txt', 'w')
        for douban_id, comment_cnt in self.comment_num_dict.items():
            output_obj.write('%s\t%s' % (douban_id, comment_cnt))


    def fetch_comments(self, douban_id):
        comment_num = 0
        output_file = os.path.join(Config.short_comment_path, douban_id)
        output_obj = open(output_file, 'w')
        with output_obj:
            start = 0
            increase_num = 1
            MAX_COMMENT_CNT = 200
            comment_hval_set = set()
            while increase_num > 0 and comment_num < MAX_COMMENT_CNT:
                increase_num = 0
                url = ('http://movie.douban.com/subject/%s/comments?start=%s&'
                        'limit=20&sort=new_score') %(douban_id, start)
                content = self.fetch_content(url)
                if content:
                    parser = HtmlParser('short_comment')
                    records = parser.parse_content(content)
                    for votes, rating, comment in records:
                        hval = hash(votes + rating + comment)
                        if not hval in comment_hval_set:
                            increase_num += 1
                            comment_num += 1
                            comment_hval_set.add(hval)
                            comment = comment.decode('utf8','ignore')\
                                    .encode('utf8')
                            output_obj.write('\t'.join([votes, \
                                    rating, comment]) + '\n')
                        if comment_num == MAX_COMMENT_CNT:
                            break
                    start += 20
        print '%s has %s comments' % (douban_id, comment_num)
        self.comment_num_dict[douban_id] = comment_num



if __name__ == '__main__':
    crawler_comment = Crawler()
    crawler_comment.multi_thread_crawl(3, 'short_comment')
    #print crawler_review.fetch_content(url)
    
