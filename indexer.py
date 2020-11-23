from parser_module import Parse
import pickle


class Indexer:
    counter = 0

    def __init__(self, corpus_path):
        self.inverted_idx = {}  # key = term , value = [postingname, index]...
        self.terms_idx = {}  # key = char , value = terms
        self.postingDict = {}
        self.config = corpus_path
        self.postingcounter = {}
        self.counter_tweetid = {}  # key=counter , value = tweetid
        self.documents = []

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        #self.documents.append(document)
        # Go over each term in the doc
        for term in document_dictionary:
            try:
                # if term == '' or str(term).isspace():
                #     continue
                posting_name = term[0]
                i = 0
                flag = False
                while not ('a' <= posting_name <= 'z' or 'A' <= posting_name <= 'Z' or '0' <= posting_name <= '9' or posting_name == '$'):
                    """
                    if i == len(term) - 1:
                        if not ('a' <= posting_name <= 'z' or 'A' <= posting_name <= 'Z' or '0' <= posting_name <= '9' or posting_name == '$'):
                            flag = True
                            break
                    """

                    i += 1
                    posting_name = str(term[i])

                if flag:
                    continue
                posting_name = term[0]
                if posting_name not in self.terms_idx.keys():
                    self.terms_idx[posting_name] = []

                self.terms_idx[posting_name].append(term)

                if term not in self.postingDict.keys():
                    self.postingDict[term] = []

                self.counter_tweetid[self.counter] = document.tweet_id

                self.postingDict[term].append([self.counter, document_dictionary[term],
                                               "%.3f" % float(document_dictionary[term] / document.doc_length)])
                self.counter += 1

                if posting_name not in self.postingcounter.keys():
                    self.postingcounter[posting_name] = 0

                if len(self.terms_idx[posting_name]) == 25000:
                    sorted_term_lst = sorted(self.terms_idx[posting_name])
                    term_lst = list(dict.fromkeys(sorted_term_lst))  # remove duplicates
                    self.terms_idx[posting_name] = []
                    self.uploadPostingFile(term_lst, posting_name)
                    # self.printPostingFile(posting_name)
                    # self.printPostingFile('documents')

            except:
                print('problem with the following key {}'.format(term[0]))

    def uploadPostingFile(self, term_lst, c):
        """
        with open(self.config + '\\' + 'documents' + '.pkl', 'ab') as f:
            pickle.dump(self.documents, f)
            self.documents.clear()
        """
        posting_name = c + str(self.postingcounter[c])
        i = 0
        for term in term_lst:
            with open(self.config + '\\' + posting_name + '.pkl', 'ab') as f:
                pickle.dump(self.postingDict[term], f)
                self.postingDict.pop(term)
            i += 1
            if term not in self.inverted_idx:
                self.inverted_idx[term] = [[posting_name, i]]
            else:
                self.inverted_idx[term].append([posting_name, i])
        self.postingcounter[c] += 1

    # def printPostingFile(self, term):
    def printPostingFile(self, c, index=0):
        posting_name = c + str(self.postingcounter[c] - 1)
        objects = []

        with (open(self.config + '\\' + posting_name + '.pkl', "rb")) as openfile:
            while True:
                try:
                    objects.append(pickle.load(openfile))
                except EOFError:
                    break

            # print(objects[index])#print specific term
            print(objects)