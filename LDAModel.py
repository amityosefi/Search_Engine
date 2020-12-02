# Set up log to external log file
import logging
import sys

import gensim

logging.basicConfig(filename='lda_model.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Set up log to terminal
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.root.addHandler(handler)

import pickle
import time
import itertools

from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.test.utils import datapath
from smart_open import open

lda_model = None


class LDA:

    def __init__(self, path):
        self.path = path
        self.docs = {}  # key=counter , value=tweetid
        self.topic_dict = {}  # key=number topic , value = [[tweetif,prob],...]
        self.counter = 0
        self.counter2 = 0

    def build_ldaModel(self):
        print("start build the model1")
        data = []
        with open(self.path + '\\documents' + '.pkl', 'rb') as handle:
            dict = pickle.load(handle)
        for tweet_id in dict:
            self.docs[self.counter] = tweet_id
            self.counter += 1
            data = data + [list(dict[tweet_id][0])]
        dictionary = Dictionary(data)

        start = time.time()
        global lda_model
        corpus = [dictionary.doc2bow(text) for text in data]
        data.clear()

        #worker
        start_worker = time.time()
        mm = gensim.corpora.MmCorpus([dictionary.doc2bow(text) for text in data])
        lda = gensim.models.ldamulticore.LdaMulticore(corpus=mm, id2word=dictionary, num_topics=15, workers=3)
        end_worker = time.time() - start_worker
        print("time takes with workers " + str(end_worker))

        start_without_worker = time.time()
        lda_model = LdaModel(corpus=corpus, num_topics=15, id2word=dictionary)
        end_without_worker = time.time() - start_without_worker
        print("time takes with workers " + str(end_without_worker))


        # print("the time takes to build the lda model is: " + str(end) + "sec")

        try:
            for i, row in enumerate(lda_model[corpus]):
                row = sorted(row, key=lambda x: (x[1]), reverse=True)
                # Get the Dominant topic, Perc Contribution and Keywords for each document
                for j, (topic_num, prop_topic) in enumerate(row):
                    if j != 0:
                        break
                    # => dominant topic
                    if prop_topic > 0.75:
                        if topic_num in self.topic_dict:
                            self.topic_dict[topic_num].append([self.docs[self.counter2], prop_topic])
                        else:
                            self.topic_dict[topic_num] = [[self.docs[self.counter2], prop_topic]]
                    # print(self.counter2)
                    self.counter2 += 1
        except:
            print('problem with the lda model')

        with open(self.path + '\\ldamodelpickle.pkl', 'wb') as f:
            pickle.dump(lda_model, f)

        lda_model.save(self.path + '\\ldamodeldatapath.pkl')

        lda_model = None

        with open(self.path + '\\ldadictionary.pkl', 'wb') as f:
            pickle.dump(dictionary, f)

        with open(self.path + '\\searcher.pkl', 'wb') as f:
            pickle.dump(self.topic_dict, f)
        self.topic_dict.clear()



        # if self.counter % 100000 != 0:  # counter != 100,000
        #     self.hundranddocs.append(document.text_tokens)
        #     self.docs[self.counter] = document.tweet_id
        #     self.counter += 1
        #     # self.dictionary = Dictionary([document.text_tokens])
        #     # self.bow_corpus = [self.dictionary.doc2bow(text) for text in self.dictionary]
        #     # self.bow_corpus.append(self.dictionary.doc2bow(document.text_tokens, allow_update=True))
        #     # self.dictionary.add_documents([document.text_tokens])
        #
        # elif self.counter == 100000:  # counter == 100,000 - for create the model
        #     self.hundranddocs.append(document.text_tokens)
        #     self.docs[self.counter] = document.tweet_id
        #     self.dictionary = Dictionary(self.hundranddocs)
        #     self.bow_corpus = [self.dictionary.doc2bow(text) for text in self.hundranddocs]
        #
        #     self.lda_model = LdaModel(self.bow_corpus, num_topics=100)
        #
        #     with open(self.path + '\\model.pkl', 'wb') as f:
        #         pickle.dump(self.lda_model, f)
        #     # with open(self.path + '\\model.pkl', 'rb') as handle:
        #     #     self.lda_model = pickle.load(handle)
        #
        #     # self.lda_model.update(self.bow_corpus)
        #     self.initialModel(self.counter)
        #     self.bow_corpus = [self.dictionary.doc2bow(doc) for doc in []]
        #
        #     self.counter += 1
        #     self.hundranddocs = []
        #
        # elif self.counter % 100000 == 0 and self.counter != 100000 and self.counter != 0:  # counter != 100,000 and counter%100,000 == 0 - for update the model
        #     self.hundranddocs.append(document.text_tokens)
        #     self.docs[self.counter] = document.tweet_id
        #     self.counter += 1
        #     self.bow_corpus = [self.dictionary.doc2bow(text) for text in self.hundranddocs]
        #     with open(self.path + '\\model.pkl', 'rb') as handle:
        #         self.lda_model = pickle.load(handle)
        #     self.lda_model.update(self.bow_corpus)
        #     self.initialModel(100000)
        #     self.bow_corpus = [self.dictionary.doc2bow(doc) for doc in []]
        #     self.hundranddocs = []