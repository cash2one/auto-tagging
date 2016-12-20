genome_dict = {}

input_obj = open('./genome')
with input_obj:
    for line in input_obj:
        fields = line.strip().split('\t')
        try:
            genome_id = int(fields[0])
            name_chs = fields[1]
            name_eng = fields[2]
            level = int(fields[3])
            father_id = int(fields[4])
            genome_dict[genome_id] = {'name': name_chs, 'level': level, 'father_id': father_id}
        except Exception, e:
            pass

used_genome = set()
used_genome_obj = open('./genome_used')
with used_genome_obj:
    for line in used_genome_obj:
        try:
            genome_id = int(line.strip())
            used_genome.add(genome_id)
        except Exception, e:
            pass

def print_tree():
    _print_tree(1, '')

def _print_tree(root_id, prefix):
    children = filter(lambda x: genome_dict[x]['father_id']==root_id, genome_dict)
    #output_str = prefix + ' +- %s' % genome_dict[root_id]['name']
    output_str = prefix + '%s:%s' % (root_id, genome_dict[root_id]['name'])
    if root_id in used_genome:
        output_str += '*'
    print output_str
    for child_id in children:
        #_print_tree(child_id, prefix + ' |  ')
        _print_tree(child_id, prefix + '  ')

def add_father(output_path):
    output_obj = open(output_path, 'w')
    genome_list = []
    for genome_id, genome_info in genome_dict.items():
        name = genome_info['name']
        father_id = genome_info['father_id']
        while father_id in genome_dict and genome_dict[father_id]['level']>1:
            father_id = genome_dict[father_id]['father_id']
        if father_id in genome_dict:
            father_name = genome_dict[father_id]['name']
        else:
            father_name = 'root'
        genome_list.append((genome_id, name, father_id, father_name))
    genome_list = sorted(genome_list, key=lambda x: x[0])
    for item in genome_list:
        output_obj.write('\t'.join([str(i) for i in item]) + '\n')



    pass

if __name__ == '__main__':
    #test()
    print_tree()
    #add_father('./genome_father')
