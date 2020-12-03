import pickle
import os.path
from  configuration import ConfigClass

def save_obj(obj, name):
    """
    This function save an object as a pickle.
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    """
    This function will load a pickle file
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def load_inverted_index():
    with open(ConfigClass.get_savedFileMainFolder() + '\\inverted_idx.pkl', 'rb') as f:
        return pickle.load(f)


def check_inverted_index(output_path):
    return os.path.isfile(output_path + '\\inverted_idx.pkl')


def check_lda(output_path):
    return os.path.isfile(output_path + '\\ldadictionary.pkl') and os.path.isfile(output_path + '\\ldamodelpickle.pkl') and os.path.isfile(output_path + '\\documents.pkl') and os.path.isfile(output_path + '\\searcher.pkl')
