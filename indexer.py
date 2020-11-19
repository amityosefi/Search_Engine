from parser_module import Parse


class Indexer:
    doc_counter = 0

    def __init__(self, config):
        self.inverted_idx = {}
        self.postingDict = {}
        self.config = config

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        self.doc_counter += 1

        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = 1
                    self.postingDict[term] = []
                else:
                    self.inverted_idx[term] += 1

                self.postingDict[term].append((document.tweet_id, document_dictionary[term]))

            except:
                print('problem with the following key {}'.format(term[0]))
"""
            if (self.doc_counter % 20000 == 0):
                for word in self.inverted_idx:
                    word = str(word)
                    lower_word = word.lower()
                    if lower_word in Parse.corpus_dict:
                        value = self.inverted_idx[word]
                        self.inverted_idx.pop(word)
                        self.inverted_idx[lower_word] = value
"""