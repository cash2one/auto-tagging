import os
class Config:
    current_path = os.path.split(os.path.realpath(__file__))[0]
    data_path = os.path.join(current_path, './Data/')
    source_data_path = os.path.join(data_path, 'source')
    derivants_data_path = os.path.join(data_path, 'derivants')
    result_path = os.path.join(data_path, 'results')


    #source data
    short_comment_path = os.path.join(source_data_path, \
            'douban/short_comment/')
    stop_word_path = os.path.join(source_data_path, 'stop_words.txt')
    db_file_path = os.path.join(source_data_path, 'db_files/')
    person_path = os.path.join(db_file_path, 'person.txt')
    genome_path = os.path.join(db_file_path, 'genome')
    used_genome_path = os.path.join(db_file_path, 'genome_used')
    id_map_path = os.path.join(db_file_path, 'id_map')
    genome_movie_path = os.path.join(db_file_path, 'genome_movie')

    #derivant data
    tf_path = os.path.join(derivants_data_path, 'tf')
    idf_path = os.path.join(derivants_data_path, 'idf.txt')
    tf_idf_path = os.path.join(derivants_data_path, 'tf_idf')
    opinion_path = os.path.join(derivants_data_path, 'opinion')
    genome_tf_path = os.path.join(derivants_data_path, 'genome_tf')
    genome_tf_idf_path = os.path.join(derivants_data_path, 'genome_tf_idf')

    #training data
    train_path = os.path.join(derivants_data_path, 'train/comment_cnt_ge_50')
    train_set_path = os.path.join(train_path + 'train_set')
    train_idf_path = os.path.join(train_path, 'idf.txt')
    train_tf_idf_path = os.path.join(train_path, 'tf_idf_normalized')
    train_genome_tf_path = os.path.join(train_path, 'genome_tf_normalized')
    train_genome_tf_idf_path = os.path.join(train_path, 'genome_tf_idf_normalized')

    #cross validatoin data
    cv_path = os.path.join(derivants_data_path, 'cv/comment_cnt_ge_50')
    cv_set_path = os.path.join(cv_path, 'cv_set')
    cv_idf_path = os.path.join(cv_path, 'idf.txt')
    cv_tf_idf_path = os.path.join(cv_path, 'tf_idf_normalized')
    tf_idf_prediction_path = os.path.join(cv_path, 'tf_idf_prediction_normalized')

    def __init__(self):
        pass

