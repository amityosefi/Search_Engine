import os
import pickle
from gensim.corpora import Dictionary
from gensim.models import LdaModel


class LDA:

    def __init__(self, path, docs, stem):
        self.path = path
        self.docs = docs  # key=counter , value=tweetid
        self.topic_dict = {}  # key=number topic , value = [[tweetif,prob],...]
        self.stem = stem
        self.counter2 = 0

    def build_ldaModel(self):
        # print("start build the model")

        data = []
        i = 0
        file_name = self.path + '\\data' + str(i) + '.pkl'
        while os.path.isfile(file_name):
            with open(file_name, 'rb') as handle:
                data += pickle.load(handle)
            os.remove(file_name)
            i += 1
            file_name = self.path + '\\data' + str(i) + '.pkl'


        dictionary = Dictionary(data)
        corpus = [dictionary.doc2bow(text) for text in data]
        data.clear()

        lda_model = LdaModel(corpus=corpus, num_topics=20, id2word=dictionary)
        # print("time takes to build the lda-model " + str(end_without_worker))

        for i, row in enumerate(lda_model[corpus]):
            row = sorted(row, key=lambda x: (x[1]), reverse=True)
            # Get the Dominant topic, Perc Contribution and Keywords for each document
            for j, (topic_num, prop_topic) in enumerate(row):
                if j >= 4:
                    break
                if prop_topic > 0.1:
                    if topic_num in self.topic_dict:
                        self.topic_dict[topic_num].append([self.docs[self.counter2], prop_topic])
                    else:
                        self.topic_dict[topic_num] = [[self.docs[self.counter2], prop_topic]]

            self.counter2 += 1

        if self.stem:
            with open('ldamodelwithstem.pkl', 'wb') as f:
                pickle.dump(lda_model, f)

            with open('ldadictionarywithstem.pkl', 'wb') as f:
                pickle.dump(dictionary, f)

            with open('ldasearcherwithstem.pkl', 'wb') as f:
                pickle.dump(self.topic_dict, f)

        else:
            with open('ldamodelwithoutstem.pkl', 'wb') as f:
                pickle.dump(lda_model, f)

            with open('ldadictionarywithoutstem.pkl', 'wb') as f:
                pickle.dump(dictionary, f)

            with open('ldasearcherwithoutstem.pkl', 'wb') as f:
                pickle.dump(self.topic_dict, f)

        self.topic_dict.clear()
