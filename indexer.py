from parser_module import Parse
import pickle
import re

class Indexer:

    def __init__(self, corpus_path):
        self.inverted_idx = {}
        self.terms_idx = {}
        self.postingDict = {}
        self.config = corpus_path
        self.postingcounter = {}


    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary

        # Go over each term in the doc
        for term in document_dictionary:
            try:
                if term == '' or str(term).isspace():
                    continue

                posting_name = term[0]
                i = 0
                flag = False
                while not ('a' <= posting_name <= 'z' or 'A' <= posting_name <= 'Z' or '0' <= posting_name <= '9'):
                    if i == len(term)-1:
                        if not ('a' <= posting_name <= 'z' or 'A' <= posting_name <= 'Z' or '0' <= posting_name <= '9'):
                            flag = True
                            break

                    i += 1
                    posting_name = str(term[i])

                if flag:
                    continue

                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = 1
                else:
                    self.inverted_idx[term] += 1

                if posting_name not in self.terms_idx.keys():
                    self.terms_idx[posting_name] = []

                self.terms_idx[posting_name].append(term)

                if term not in self.postingDict.keys():
                    self.postingDict[term] = []

                self.postingDict[term].append([document.tweet_id, document_dictionary[term],
                                               float(document_dictionary[term] / document.doc_length)])

                if posting_name not in self.postingcounter.keys():
                    self.postingcounter[posting_name] = 0

                if (len(self.terms_idx[posting_name]) == 5000):
                    sorted_term_lst = sorted(self.terms_idx[posting_name])
                    term_lst = list(dict.fromkeys(sorted_term_lst)) #remove duplicates
                    self.terms_idx[posting_name] = []
                    self.uploadPostingFile(term_lst, posting_name)

            except:
                print('problem with the following key {}'.format(term[0]))

    def uploadPostingFile(self, term_lst, c):
        posting_name = c + str(self.postingcounter[c])
        for term in term_lst:
            with open(self.config + '\\' + posting_name + '.pkl', 'ab') as f:
                pickle.dump(self.postingDict[term], f)
                self.postingDict.pop(term)
            #self.inverted_idx[term].append()

            """
            objects = []
            with (open(self.config + '\\' + posting_name + '.pkl', "rb")) as openfile:
                while True:
                    try:
                        objects.append(pickle.load(openfile))
                    except EOFError:
                        break
            ##print(objects)
            """
        self.postingcounter[c] += 1
