import pickle
import time
import itertools
from pprint import pprint

from gensim import similarities
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from smart_open import open


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
        # print("start build the model2")
        class MyCorpus:
            def __iter__(self):
                for line in data:
                    doc = dictionary.doc2bow(line)
                    if len(doc) < 1:
                        continue
                    yield doc

        start = time.time()
        # print("start build the model3")
        lda_model = LdaModel(corpus=MyCorpus(), num_topics=100, id2word=dictionary)
        end = time.time() - start
        print("the time takes to build the lda model is: " + str(end) + "sec")

        with open(self.path + '\\ldamodel.pkl', 'wb') as f:
            pickle.dump(lda_model, f)

        with open(self.path + '\\ldadictionary.pkl', 'wb') as f:
            pickle.dump(dictionary, f)

        for batch in grouper(MyCorpus(), 50000):
            # approach 1:
            # batch_topics = list(filter(partial(is_not, None), batch))
            # index_matrix = similarities.MatrixSimilarity(self.lda_model[batch])
            # print(index_matrix.index[3][3])
            # pprint(lda_model.show_topics(formatted=False))
            try:
                for i, row in enumerate(lda_model[batch]):
                    row = sorted(row, key=lambda x: (x[1]), reverse=True)
                    # Get the Dominant topic, Perc Contribution and Keywords for each document
                    for j, (topic_num, prop_topic) in enumerate(row):
                        if j != 0:
                            break
                          # => dominant topic
                        if prop_topic > 0.7:
                            if topic_num in self.topic_dict:
                                self.topic_dict[topic_num].append([self.docs[self.counter2], prop_topic])
                            else:
                                self.topic_dict[topic_num] = [[self.docs[self.counter2], prop_topic]]
                        print(self.counter2)
                        self.counter2 += 1
            except:
                print('problem with the lda model')

                        # wp = lda_model.show_topic(topic_num)
                        # print(wp)
                        # x= 6

            # y = batch
            # for docID in range(75906):
            #     topic_vector = lda_model[MyCorpus[docID]]
            #
            #     for topicID, prob in topic_vector:
            #         if prob > 0.7:
            #             self.topic_dict[topicID].append((docID, prob))

        x = 8
        with open(self.path + '\\searcher.pkl', 'wb') as f:
            pickle.dump(self.topic_dict, f)
        self.topic_dict.clear()

        # print(batch_topics)

        # for docID in range(counter):
        #     topic_vector = self.lda_model[MyCorpus()[docID]]
        #     for topicID, prob in topic_vector:
        #         if prob > 0.7:
        #             if topicID in self.topic_dict:
        #                 self.topic_dict[topicID].append([self.docs[docID], prob])
        #             else:
        #                 self.topic_dict[topicID] = [[self.docs[docID], prob]]

        # you'd need to do something with these docs here, but I'm just breaking
        # break

    def upload_model(self):
        with open(self.path + '\\ldamodel.pkl', 'rb') as handle:
            return pickle.load(handle)

    # def initialModel(self, number):
    #
    #     print("start load the LDA modle")
    #     start = time.time()
    #     # objects = []
    #     # for i in range(self.numoffiles - 1):
    #     #     with (open(self.output_path + '\\lda' + str(i) + '.pkl', "rb")) as openfile:
    #     #         while True:
    #     #             try:
    #     #                 objects.append(pickle.load(openfile))
    #     #             except EOFError:
    #     #                 break
    #     #
    #     # objects.append(self.tempdocs)
    #     # self.tempdocs.clear()
    #     # i = 0
    #     # while i < len(objects):
    #     #     j = 0
    #     #     while j < len(objects[i]):
    #     #         self.bow_corpus.append(self.dictionary.doc2bow(objects[i][j], allow_update=True))
    #     #         j += 1
    #     #     i += 1
    #     #
    #     #
    #     # print("the len of the corpus lda is: " + str(len(objects)))
    #     # objects.clear()
    #
    #     # self.lda_model = gensim.models.LdaMulticore(self.bow_corpus, 50, self.dictionary)
    #
    #     # self.lda_model.update()
    #
    #     # for i in range(5):
    #     #     print(self.lda_model.show_topic(i))
    #     # i = 0
    #     # for i in range(8):
    #     #     for index, score in sorted(self.lda_model[self.bow_corpus[i]], key=lambda tup: -1 * tup[1]):
    #     #         print("\nScore: {}\t \nTopic: {}".format(score, self.lda_model.print_topic(index, 10)))
    #     #     print(i)
    #     #     i += 1\
    #
    #     for docID in range(number):
    #         topic_vector = self.lda_model[self.bow_corpus[docID]]
    #         for topicID, prob in topic_vector:
    #             if prob > 0.7:
    #                 if topicID in self.topic_dict:
    #                     self.topic_dict[topicID].append([self.docs[docID], prob])
    #                 else:
    #                     self.topic_dict[topicID] = [[self.docs[docID], prob]]
    #
    #     # temp_file = datapath(self.output_path + "\\model")
    #     # self.lda_model.save(temp_file)
    #     with open(self.path + '\\model.pkl', 'wb') as f:
    #         pickle.dump(self.lda_model, f)
    #     self.lda_model = None
    #
    #     # for docID in range(self.counter - 100000 - 1):
    #     #     topic_vector = self.lda_model[other_corpus[docID]]
    #     #     for topicID, prob in topic_vector:
    #     #         if prob > 0.7:
    #     #             if topicID in topic_dict:
    #     #                 topic_dict[topicID].append([self.docs[docID], prob])
    #     #             else:
    #     #                 topic_dict[topicID] = [[self.docs[docID], prob]]
    #
    #     # f = open(path + '\\searcher.pkl', "wb")
    #     # pickle.dump(self.topic_dict, f)
    #     # f.close()
    #
    #     # topic_dict = {}
    #     # i = 0
    #     # for docID in range(70000):
    #     #     print(i)
    #     #     topic_vector = self.lda_model[self.bow_corpus[docID]]
    #     #     for topicID, prob in topic_vector:
    #     #         if prob > 0.9:
    #     #             if topicID in topic_dict:
    #     #                 topic_dict[topicID].append([self.docs[docID], prob])
    #     #                 if len(topic_dict[topicID]) == 300:
    #     #                     with (open(self.output_path + '\\topic' + str(topicID) + '_' + str(self.topicsize[topicID]) + '.pkl', "wb")) as openfile:
    #     #                         pickle.dump(topic_dict[topicID], openfile)
    #     #                     self.topicsize[topicID] += 1
    #     #                     topic_dict[topicID].clear()
    #     #             else:
    #     #                 topic_dict[topicID] = [[self.docs[docID], prob]]
    #     #                 self.topicsize[topicID] = 0
    #     #     i += 1
    #     #
    #     # for docID in range(5906-1):
    #     #     print(i)
    #     #     topic_vector = self.lda_model[other_corpus[docID]]
    #     #     for topicID, prob in topic_vector:
    #     #         if prob > 0.9:
    #     #             if topicID in topic_dict:
    #     #                 topic_dict[topicID].append([self.docs[docID], prob])
    #     #                 if len(topic_dict[topicID]) == 300:
    #     #                     with (open(self.output_path + '\\topic' + str(topicID) + '_' + str(self.topicsize[topicID]) + '.pkl', "wb")) as openfile:
    #     #                         pickle.dump(topic_dict[topicID], openfile)
    #     #                     self.topicsize[topicID] += 1
    #     #                     topic_dict[topicID].clear()
    #     #             else:
    #     #                 topic_dict[topicID] = [[self.docs[docID], prob]]
    #     #                 self.topicsize[topicID] = 0
    #     #     i += 1
    #     #
    #     # f = open(path + '\\searcher.pkl', "wb")
    #     # pickle.dump(topic_dict, f)
    #     # f.close()
    #     end = time.time() - start
    #     print("end load the LDA modle in: " + str(end) + " sec")
    #     # print("topic 0 with :" + str(len(self.topic_dict[0])) + " docs")
    #     # print("topic 1 with :" + str(len(self.topic_dict[1])) + " docs")
    #     # print("topic 2 with :" + str(len(self.topic_dict[2])) + " docs")
    #
    #     # self.topic_dict.clear()
    #
    # def upload_the_seracher(self):
    #
    #     self.bow_corpus = [self.dictionary.doc2bow(text) for text in self.hundranddocs]
    #     with open(self.path + '\\model.pkl', 'rb') as handle:
    #         self.lda_model = pickle.load(handle)
    #     self.lda_model.update(self.bow_corpus)
    #     self.initialModel(len(self.hundranddocs))
    #     self.bow_corpus = [self.dictionary.doc2bow(doc) for doc in []]
    #
    #     with open(self.path + '\\searcher.pkl', 'wb') as f:
    #         pickle.dump(self.topic_dict, f)
    #
    #     self.topic_dict.clear()
    #     self.dictionary = None
    #     self.lda_model = None


def grouper(iterable, n, fillvalue=None):  # corpus, n=batches
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)
