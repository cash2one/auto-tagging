import sys
sys.path.append('..')
from DAL.MySqlDAL import MySqlDAL
import re

def get_id_map(result_file):
    mysql_dal = MySqlDAL('Final')
    sql_cmd = 'select works_id, douban_url from movie_final'
    result = mysql_dal.select(sql_cmd)
    output_obj = open(result_file, 'w')
    with output_obj:
        for line in result:
            try:
                works_id = int(line[0])
                url = line[1]
                m = re.match(r'http://movie.douban.com/subject/(\d+)/', url)
                douban_id = int(m.group(1))
                output_obj.write('%s\t%s\n' % (works_id, douban_id))
            except Exception, e:
                pass



if __name__ == '__main__':
    id_map_file = '../Data/source/db_files/id_map'
    get_id_map(id_map_file)
