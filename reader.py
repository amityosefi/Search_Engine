import os
from datetime import datetime

import pandas as pd


class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_file(self, file_name):
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.

        """

        full_path = os.path.join(self.corpus_path, file_name)
        df = pd.read_parquet(full_path, engine="pyarrow")

        return df.values.tolist()

    def read_dir(self):

        documents_list = []
        directories = os.listdir(self.corpus_path)
        for i in range(len(directories)):
            if not directories[i].endswith('DS_Store'):
                for name in os.listdir(self.corpus_path + '\\' + directories[i]):
                    # print(datetime.now())
                    if name.endswith('parquet'):
                        full_name = directories[i] + '\\' + name
                        documents_list.extend(self.read_file(full_name))
                        print(str(name))

        print("finish read")
        return documents_list
