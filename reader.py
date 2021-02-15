import os

import pandas as pd


class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path
        self.docsfiles = {}

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
            if directories[i].endswith('parquet'):
                filename = directories[i]
                full_name = self.corpus_path + '\\' + filename
                if full_name in self.docsfiles:
                    continue
                self.docsfiles[full_name] = ''
                return self.read_file(full_name)
            else:  # it is a dir
                if not directories[i].endswith('DS_Store'):
                    for filename in os.listdir(self.corpus_path + '\\' + directories[i]):
                        if filename.endswith('parquet'):
                            full_name = directories[i] + '\\' + filename
                            if full_name in self.docsfiles:
                                continue
                            self.docsfiles[full_name] = ''
                            return self.read_file(full_name)
        return documents_list