from parser_module import Parse
import pickle

class Indexer:
    doc_counter = 0

    def __init__(self, corpus_path):
        self.inverted_idx = {} # key=term , value=counter of appearance in tweets
        self.postingDict = {} #
        self.config = corpus_path
        self.postingcounter = {} # key=char , value=counter of terms starting with specific char


    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        document_dictionary = document.term_doc_dictionary
        # self.doc_counter += 1
        # Go over each term in the doc
        # print(document_dictionary)
        # print(document_dictionary.keys())
        for term in document_dictionary.keys():
            try:
                if term == '':
                    continue
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = 1
                    self.postingcounter[term[0]] = 1
                else:
                    self.inverted_idx[term] += 1
                    self.postingcounter[term[0]] += 1

                posting_name = str(term[0]).lower()
                # if posting_name not in self.postingDict.keys():
                #     self.postingcounter += 1
                # else:
                #     self.postingcounter += 1


                self.postingDict[term] = [document.tweet_id, document_dictionary[term],
                                               float(document_dictionary[term] / document.doc_length)]
                # print(self.postingDict)
                if self.postingcounter[term[0]] == 100:
                    self.uploadPostingFile(term[0])

            except:
                print('problem with the following key {}'.format(term[0]))








    def uploadPostingFile(self, c):
        for term in self.postingDict:
            posting_name = str(c).lower()
            self.postingcounter[posting_name] = 0
            with open(self.config + '\\' + posting_name + '.pkl', 'ab') as f:
                pickle.dump(self.postingDict[term], f)


            # use this program to see what is inside the posting file posting file
            objects = []
            with (open(self.config + '\\' + posting_name + '.pkl', "rb")) as openfile:
                while True:
                    try:
                        objects.append(pickle.load(openfile))
                    except EOFError:
                        break
            print(objects)
        self.postingDict.clear()
'''
        if self.doc_counter // 200 == 0:
            x = 5
            for term in self.postingDict:
                posting_name = str(term).lower()

                # self.postingcounter[posting_name] += 1
#                 posting_name += str(self.postingcounter[posting_name][1])
                with open(self.config + '\\' + posting_name + '.pkl', 'wb') as f:
                    pickle.dump(self.postingDict[term], f)
            self.postingDict.clear()
            self.doc_counter = 0
'''

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