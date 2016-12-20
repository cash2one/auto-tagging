#-*- encoding: utf-8 -*-

from time import sleep
from functools import wraps
import urllib2, logging

class Crawler:
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

if __name__ == '__main__':
    url = 'http://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&page_limit=20&page_start=0'
    crawler_review = Crawler()
    print crawler_review.fetch_content(url)
