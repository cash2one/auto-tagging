import sys
sys.path.append('..')
from BLL.Train import Train
from BLL.CrossValidation import CrossValidation
from Config import Config


if __name__=='__main__':
    Train.tf_idf_training(50, 0.7)
    cv_set = CrossValidation.get_cv_set()
    CrossValidation.get_prediction(cv_set, Config.tf_idf_prediction_path)
    CrossValidation.evaluation(Config.tf_idf_prediction_path)
