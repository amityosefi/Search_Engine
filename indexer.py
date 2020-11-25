from pprint import pprint

import gensim
from gensim import corpora

from parser_module import Parse
import pickle
import os


class Indexer:
    counter = 0

    def __init__(self, corpus_path):
        self.inverted_idx = {}  # key = term , value = [postingname, index]...
        self.terms_idx = {}  # key = char , value = terms
        self.postingDict = {}
        self.config = corpus_path
        self.postingcounter = {}
        self.documents = []

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary

        # self.documents.append(document)
        # Go over each term in the doc
        # texts = [document.text_tokens]
        # id2word = corpora.Dictionary(texts)
        # corpus = [id2word.doc2bow(text) for text in texts]
        # # print([[(id2word[id], freq) for id, freq in cp] for cp in corpus[:1]])
        # lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
        #                                             id2word=id2word,
        #                                             num_topics=5,
        #                                             random_state=100,
        #                                             update_every=1,
        #                                             chunksize=100,
        #                                             passes=10,
        #                                             alpha='auto',
        #                                             per_word_topics=True)
        #
        # pprint(lda_model.print_topics(num_topics=5, num_words=3))





        #self.documents.append(document)
        # Go over each term in the doc
        for term in document_dictionary:
            try:
                # if term == '' or str(term).isspace():
                #     continue
                posting_name = self.find_posting_name(term)

                if posting_name not in self.terms_idx:
                    self.terms_idx[posting_name] = []

                self.terms_idx[posting_name].append(term)

                if term not in self.postingDict:
                    self.postingDict[term] = []

                if document.doc_length > 0:
                    self.postingDict[term].append([document.tweet_id, document_dictionary[term],
                                               "%.3f" % float(document_dictionary[term] / document.doc_length)])
                else:
                    self.postingDict[term].append([document.tweet_id, document_dictionary[term], 0.9])

                if posting_name not in self.postingcounter:
                    self.postingcounter[posting_name] = 0

                if len(self.terms_idx[posting_name]) == 25000:
                    #sorted_term_lst = sorted(self.terms_idx[posting_name])
                    term_lst = list(dict.fromkeys(self.terms_idx[posting_name]))  # remove duplicates
                    self.terms_idx[posting_name] = []
                    self.uploadPostingFile(term_lst, posting_name)
                    self.printPostingFile(posting_name)
                    # self.printPostingFile('documents')

            except:
                print('problem with the following key {}'.format(term[0]))

    def find_posting_name(self, term):

        posting_name = str(term[0]).lower()
        i = 0
        while not (
                'a' <= posting_name <= 'z' or '0' <= posting_name <= '9' or posting_name == '$'):
            """
            if i == len(term) - 1:
                if not ('a' <= posting_name <= 'z' or 'A' <= posting_name <= 'Z' or '0' <= posting_name <= '9' or posting_name == '$'):
                    flag = True
                    break
            """

            i += 1
            posting_name = str(term[i]).lower()

        return posting_name

    def uploadPostingFile(self, term_lst, c):
        """
        with open(self.config + '\\' + 'documents' + '.pkl', 'ab') as f:
            pickle.dump(self.documents, f)
            self.documents.clear()
        """
        posting_name = c + str(self.postingcounter[c])
        dic = {}
        for term in term_lst:
            dic[term] = self.postingDict[term]
            self.postingDict.pop(term)

        f = open(self.config + '\\' + posting_name + '.pkl', 'wb')
        pickle.dump(dic, f)
        f.close()

        self.postingcounter[c] += 1

    # def printPostingFile(self, term):
    def printPostingFile(self, c, index=0):
        posting_name = c + str(self.postingcounter[c] - 1)
        objects = {}

        with (open(self.config + '\\' + posting_name + '.pkl', "rb")) as openfile:
            while True:
                try:
                    objects = pickle.load(openfile)
                except EOFError:
                    break

            #print(objects[index])#print specific term
            #print(objects)

    def merge_posting_files(self):

        for key in self.terms_idx:
            if (self.terms_idx[key] == []):
                continue
            sorted_term_lst = sorted(self.terms_idx[key])
            term_lst = list(dict.fromkeys(sorted_term_lst))
            dic = {}
            for term in term_lst:
                dic[term] = self.postingDict[term]
                self.postingDict.pop(term)
            posting_name = key + str(self.postingcounter[key])
            f = open(self.config + '\\' + posting_name + '.pkl', 'ab')
            pickle.dump(dic, f)
            f.close()

        for posting_name in self.postingcounter:
            merged_dict = {}
            objects = {}
            posting_lst = self.find_posting_files(posting_name)
            for file in posting_lst:
                with (open(file, "rb")) as openfile:
                    while True:
                        try:
                            objects = pickle.load(openfile)
                        except EOFError:
                            break
                os.remove(file)
                for term in objects:
                    lower_term = str(term).lower()
                    temp = term
                    if lower_term in Parse.corpus_dict:
                        temp = lower_term
                    if temp not in merged_dict:
                        merged_dict[temp] = []
                    merged_dict[temp].extend(objects[term])

            merged_file = open(self.config + '\\' + posting_name + '.pkl', "wb")
            pickle.dump(objects, merged_file)
            merged_file.close()

    def find_posting_files(self, posting_name):
        posting_lst = []
        num_of_posting = self.postingcounter[posting_name] + 1
        for i in range(num_of_posting):
            file_path = self.config + '\\' + posting_name + str(i) + '.pkl'
            posting_lst.append(file_path)

        return posting_lst