# Set up log to external log file
import logging
import os
import sys


# logging.basicConfig(filename='lda_model.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
#
# # Set up log to terminal
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logging.root.addHandler(handler)

import pickle
import time

from gensim.corpora import Dictionary
from gensim.models import LdaModel
# from smart_open import open

lda_model = None


class LDA:

    def __init__(self, path, docs, stem):
        self.path = path
        self.docs = docs  # key=counter , value=tweetid
        self.topic_dict = {}  # key=number topic , value = [[tweetif,prob],...]
        self.stem = stem
        self.counter2 = 0

    def build_ldaModel(self):
        # print("start build the model")

        with open(self.path + '\\data' + '.pkl', 'rb') as handle:
            data = pickle.load(handle)

        os.remove(self.path + '\\data' + '.pkl')

        dictionary = Dictionary(data)
        corpus = [dictionary.doc2bow(text) for text in data]
        data.clear()

        start_without_worker = time.time()
        global lda_model
        lda_model = LdaModel(corpus=corpus, num_topics=20, id2word=dictionary)
        end_without_worker = time.time() - start_without_worker
        # print("time takes to build the lda-model " + str(end_without_worker))

        # try:
        for i, row in enumerate(lda_model[corpus]):
            row = sorted(row, key=lambda x: (x[1]), reverse=True)
            # if self.counter2 == 238085:
            #     x = 9
            # Get the Dominant topic, Perc Contribution and Keywords for each document
            for j, (topic_num, prop_topic) in enumerate(row):
                if j >= 4:
                    break
                # => dominant topic
                # if prop_topic > 0.6:
                if topic_num in self.topic_dict:
                    self.topic_dict[topic_num].append([self.docs[self.counter2], prop_topic])
                else:
                    self.topic_dict[topic_num] = [[self.docs[self.counter2], prop_topic]]
                # print(self.counter2)
            self.counter2 += 1
        # except:
        #     print('problem with the lda model')

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


    def add_docs_to_model(self, counter):
        data = []
        for i in range(counter):
            with open(self.path + '\\data' + str(i) + '.pkl', 'rb') as handle:
                data += pickle.load(handle)

            os.remove(self.path + '\\data' + str(i) + '.pkl')


        if self.stem:
            with open('ldamodelwithstem.pkl', 'rb') as handle:
                lda_model = pickle.load(handle)

            with open('ldadictionarywithstem.pkl', 'rb') as handle:
                dictionary = pickle.load(handle)

        else:
            with open('ldamodelwithoutstem.pkl', 'rb') as handle:
                lda_model = pickle.load(handle)

            with open('ldadictionarywithoutstem.pkl', 'rb') as handle:
                dictionary = pickle.load(handle)

        self.counter2 = 0
        for document in data:
            new_query_tokens = []
            for token in document:
                if not ('@' in token or '#' in token or '$' in token or '%' in token):
                    token = token.lower()
                new_query_tokens.append(token)

            new_bow = dictionary.doc2bow(new_query_tokens)
            topic_vector = lda_model.get_document_topics(bow=new_bow)

            row = sorted(topic_vector, key=lambda x: (x[1]), reverse=True)

            for j, (topic_num, prop_topic) in enumerate(row):
                if j >= 3:
                    break
                if prop_topic > 0.3:
                    if topic_num in self.topic_dict:
                        self.topic_dict[topic_num].append([self.docs[self.counter2], prop_topic])
                    else:
                        self.topic_dict[topic_num] = [[self.docs[self.counter2], prop_topic]]

            self.counter2 += 1
            if self.counter2 % 250000 == 0:
                print(self.counter2)


        with (open('searcher.pkl', 'wb')) as handle:
            pickle.dump(self.topic_dict, handle)

        self.topic_dict.clear()
