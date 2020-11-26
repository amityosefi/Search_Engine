from pprint import pprint
import gensim
from gensim import corpora

from LDAModel import LDA
from parser_module import Parse
import pickle
import os
import math


class Indexer:

    def __init__(self, corpus_path):
        self.inverted_idx = {}  # key = term , value = [postingname, index]...
        self.terms_idx = {}  # key = char , value = terms
        self.postingDict = {}
        self.config = corpus_path
        self.postingcounter = {}
        self.documents = {}
        self.doc_counter = 0
        self.lda = LDA()

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary

        self.documents[self.doc_counter] = [document.tweet_id, document.max_tf, document.num_of_unique_words]
        self.doc_counter += 1

        self.lda.addDoc(document)
        #self.documents.append(document)
        # Go over each term in the doc
        for term in document_dictionary:
            try:
                # if term == '' or str(term).isspace():
                #     continue

                if term not in self.inverted_idx:
                    self.inverted_idx[term] = 1
                else:
                    self.inverted_idx[term] += 1

                posting_name = self.find_posting_name(term)

                if posting_name not in self.terms_idx:
                    self.terms_idx[posting_name] = []

                self.terms_idx[posting_name].append(term)

                if term not in self.postingDict:
                    self.postingDict[term] = []

                if document.doc_length > 0:
                    self.postingDict[term].append([document.tweet_id, document_dictionary[term],
                                               "%.3f" % float(document_dictionary[term] / document.doc_length)]) #tf
                else:
                    self.postingDict[term].append([document.tweet_id, document_dictionary[term], 0.9])

                if posting_name not in self.postingcounter:
                    self.postingcounter[posting_name] = 0

                if len(self.terms_idx[posting_name]) == 25000:
                    #sorted_term_lst = sorted(self.terms_idx[posting_name])
                    term_lst = list(dict.fromkeys(self.terms_idx[posting_name]))  # remove duplicates
                    self.terms_idx[posting_name] = []
                    self.uploadPostingFile(term_lst, posting_name)
                    # self.printPostingFile('documents')

            except:
                print('problem with the following key {}'.format(term[0]))

    def find_posting_name(self, term):

        term = str(term)

        if '$' in term or '%' in term:
            posting_name = 'delimiters'
        else:
            posting_name = term[0].lower()
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
        temp_term_dict = {}
        for term in term_lst:
            temp_term_dict[term] = self.postingDict[term]
            self.postingDict.pop(term)

        f = open(self.config + '\\' + posting_name + '.pkl', 'wb')
        pickle.dump(temp_term_dict, f)
        f.close()

        self.postingcounter[c] += 1

    def merge_posting_files(self):

        num_of_documents = len(self.documents)

        common_terms = self.find_common_terms()
        common_terms_dict = {}

        self.add_the_rest_terms()

        for posting_name in self.postingcounter:
            merged_dict = {}
            objects = {}
            posting_lst = self.find_posting_files(posting_name)
            #if len(posting_lst) == 1:
             #   continue
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

                    if temp in common_terms:
                        common_terms_dict[temp] = objects[term]
                        common_terms_dict[temp].extend([math.log2(num_of_documents / self.inverted_idx[term])])  #idf
                    else:
                        merged_dict[temp] = objects[term]
                        merged_dict[temp].extend([math.log2(num_of_documents/self.inverted_idx[term])]) #idf

            merged_file = open(self.config + '\\' + posting_name + '.pkl', "wb")
            pickle.dump(merged_dict, merged_file)
            merged_file.close()

        common_terms_file = open(self.config + '\\' + 'common.pkl', "wb")
        pickle.dump(common_terms_dict, common_terms_file)
        merged_file.close()

        docs_file = open(self.config + '\\' + 'documents.pkl', "wb")
        pickle.dump(self.documents, docs_file)
        merged_file.close()

    def find_posting_files(self, posting_name):
        posting_lst = []
        num_of_posting = self.postingcounter[posting_name] + 1
        for i in range(num_of_posting):
            file_path = self.config + '\\' + posting_name + str(i) + '.pkl'
            posting_lst.append(file_path)

        return posting_lst

    def find_common_terms(self):
        sorted_terms = sorted(self.inverted_idx, key=self.inverted_idx.get, reverse=True)
        first_20 = int(0.2 * len(sorted_terms))
        return sorted_terms[:first_20]

    def add_the_rest_terms(self):
        for key in self.terms_idx:
            if (self.terms_idx[key] == []):
                continue
            term_lst = list(dict.fromkeys(self.terms_idx[key]))
            temp_term_dict = {}
            for term in term_lst:
                temp_term_dict[term] = self.postingDict[term]
                self.postingDict.pop(term)
            posting_name = key + str(self.postingcounter[key])
            f = open(self.config + '\\' + posting_name + '.pkl', 'ab')
            pickle.dump(temp_term_dict, f)
            f.close()