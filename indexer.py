from parser_module import Parse
import pickle

class Indexer:
    doc_counter = 0

    def __init__(self, corpus_path):
        self.inverted_idx = {}
        self.postingDict = {}
        self.config = corpus_path
        self.postingcounter = {}


    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -

        document_dictionary = document.term_doc_dictionary

        self.doc_counter += 1
        # Go over each term in the doc
        for term in document_dictionary:
            ##print(document_dictionary)
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = 1
                    self.postingDict[term] = []
                else:
                    self.inverted_idx[term] += 1

                posting_name = str(term[0]).lower()
                if posting_name not in self.postingDict.keys():
                    self.postingcounter[posting_name] = (1,0)
                else:
                    self.postingcounter[posting_name][0] += 1

                self.postingDict[term].append([document.tweet_id, document_dictionary[term],
                                               float(document_dictionary[term] / document.doc_length)])

                ##print(self.postingDict)

            except:
                print('problem with the following key {}'.format(term[0]))

        if (self.doc_counter % 200 == 0):
            for term in self.postingDict:
                posting_name = str(term[0]).lower()
                if (self.postingcounter[posting_name][0] == 10000):
                    self.postingcounter[posting_name][1] += 1
                    posting_name += str(self.postingcounter[posting_name][1])
                    with open(self.config + '\\' + posting_name + '.pkl', 'wb') as f:
                        pickle.dump(self.postingDict[term], f)
                else:
                    with open(self.config + '\\' + posting_name + '.pkl', 'wb') as f:
                        pickle.dump(self.postingDict[term], f)
                self.postingcounter[posting_name][0] += 1

            self.postingDict.clear()

            if (self.doc_counter % 20000 == 0):
                for word in self.inverted_idx:
                    word = str(word)
                    lower_word = word.lower()
                    if lower_word in Parse.corpus_dict:
                        value = self.inverted_idx[word]
                        self.inverted_idx.pop(word)
                        self.inverted_idx[lower_word] = value
     """