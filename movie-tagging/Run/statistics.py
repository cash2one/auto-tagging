import sys
sys.path.append('..')
from Config import Config
import os

root = Config.short_comment_path
douban_ids = os.listdir(root)
comment_cnt_hist = {}
for douban_id in douban_ids:
    input_obj = open(os.path.join(root, douban_id))
    with input_obj:
        line_cnt = len(input_obj.readlines())
        comment_cnt_hist[line_cnt] = comment_cnt_hist.get(line_cnt, 0) + 1

output_obj = open('./comment_cnt_hist.txt', 'w')
comment_cnt_list = sorted(comment_cnt_hist.items(), key=lambda x: x[0])
for k, v in comment_cnt_list:
    output_obj.write('%s\t%s\n' % (k, v))
    
