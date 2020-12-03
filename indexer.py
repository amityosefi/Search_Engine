import pickle
import os


class Indexer:

    def __init__(self, output_path):
        #self.inverted_idx = {}  # key = term , value = count the documents that the term exist
        self.terms_idx = {}  # key = char , value = terms
        self.postingDict = {} # key = term, value = tf, idf
        self.config = output_path
        self.postingcounter = {} # key = letters, value = count posting files from each letter
        self.documents_idx = {} # key = last digit of each tweet id, key = dict of documents with the same digit
        self.documentsCounter = {} # key = numbers of docs, value = count posting files from each doc
        self.documents = {} # key = tweet id , value = term dict, max_tf, num of unique words
        self.numberToCharDict = {'0': 'a', '1': 'b', '2': 'c', '3': 'd', '4': 'e', '5': 'f', '6': 'g', '7': 'h', '8': 'i', '9': 'j'}
        #self.doc_counter = 0
        self.count = 0
        self.inverted_idx = {}

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        print(self.count)
        self.count += 1

        document_dictionary = document.term_doc_dictionary
        documentsTempDict = {}
        documentsTempDict[document.tweet_id] = [document_dictionary, document.max_tf, document.num_of_unique_words]
        document_name = document.tweet_id[len(document.tweet_id)-1]
        if document_name not in self.documents_idx:
            self.documents_idx[document_name] = {}
        self.documents_idx[document_name].update(documentsTempDict)
        if document_name not in self.documentsCounter:
            self.documentsCounter[document_name] = 0
        if len(self.documents_idx[document_name]) == 100000:
            self.uploadDocumnetToPostingFile(document_name)
            self.documentsCounter[document_name] += 1

        #self.doc_counter += 1
        #self.lda.addDoc(document)

        # Go over each term in the doc
        for term in document_dictionary:
            try:
                # if term == '' or str(term).isspace():
                #     continue

                if term not in self.inverted_idx:
                    self.inverted_idx[term] = 1
                else:
                    self.inverted_idx[term] += 1

                #self.inverted_idx[term].append(document.tweet_id)

                posting_name = self.find_posting_name(term)

                if posting_name not in self.terms_idx:
                    self.terms_idx[posting_name] = []

                self.terms_idx[posting_name].append(term)

                if term not in self.postingDict:
                    self.postingDict[term] = {}

                term_dict = {}

                if document.doc_length > 0:
                    term_dict[document.tweet_id] = "%.3f" % float(document_dictionary[term] / document.max_tf) #tf
                else:
                    term_dict[document.tweet_id] = 0.9 #tf

                self.postingDict[term].update(term_dict)

                if posting_name not in self.postingcounter:
                    self.postingcounter[posting_name] = 0

                if len(self.terms_idx[posting_name]) == 200000:
                    #sorted_term_lst = sorted(self.terms_idx[posting_name])
                    term_lst = list(dict.fromkeys(self.terms_idx[posting_name]))  # remove duplicates
                    self.terms_idx[posting_name] = []
                    self.uploadTokensToPostingFile(term_lst, posting_name)
                    self.postingcounter[posting_name] += 1
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

    def uploadDocumnetToPostingFile(self, c):

        document_name = "doc" + self.numberToCharDict[c] + str(self.documentsCounter[c])
        f = open(self.config + '\\' + document_name + '.pkl', 'wb')
        pickle.dump(self.documents_idx[c], f)
        f.close()
        self.documents_idx[c] = {}

        # file_path = self.config + '\\' + document_name + '.pkl'
        # documents_name_dict = {}
        # with (open(file_path, "rb")) as openfile:
        #     while True:
        #         try:
        #             documents_name_dict = pickle.load(openfile)
        #         except EOFError:
        #             break
        # print(documents_name_dict)
        # print("h")

    def uploadTokensToPostingFile(self, term_lst, c):
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


    def merge_posting_files(self):


        self.uploadDocumentsFromPosting()
        num_of_documents = len(self.documents)

        merged_dict = {}

        for posting_name in self.postingcounter:
            posting_name_dict = {}
            new_posting_name_dict = {}
            posting_lst = self.find_posting_files(posting_name)
            len_of_posting_list = len(posting_lst)
            i = 0
            while (i < len_of_posting_list):

                if self.terms_idx[posting_name] != []:
                    term_lst = list(dict.fromkeys(self.terms_idx[posting_name]))
                    for term in term_lst:
                        posting_name_dict[term] = self.postingDict[term]
                        self.postingDict.pop(term)
                    self.terms_idx[posting_name] = []
                else:
                    with (open(posting_lst[i], "rb")) as openfile:
                        while True:
                            try:
                                posting_name_dict = pickle.load(openfile)
                            except EOFError:
                                break
                    try:
                        os.remove(posting_lst[i])
                    except:
                        print("no such a file of name" + str(posting_name))
                    i += 1

                for term in posting_name_dict:

                    # if term in merged_dict:
                    #     continue

                    lower_term = str(term).lower()
                    if (term != lower_term) and (lower_term in self.inverted_idx):
                        if lower_term not in new_posting_name_dict:
                            new_posting_name_dict[lower_term] = {}
                        if lower_term in posting_name_dict:
                             new_posting_name_dict[lower_term].update(posting_name_dict[lower_term])

                        for doc_id in posting_name_dict[term]:
                            val = self.documents[doc_id][0][term]
                            # print(self.documents[doc_id][0])
                            if lower_term in self.documents[doc_id][0]:
                                self.documents[doc_id][0][lower_term] += val
                            else:
                                self.documents[doc_id][0][lower_term] = val
                                self.inverted_idx[lower_term] += 1
                            self.documents[doc_id][0].pop(term)

                            new_val = self.documents[doc_id][0][lower_term]
                            current_max_tf = self.documents[doc_id][1]
                            if current_max_tf < new_val:
                                self.documents[doc_id][1] = new_val

                            new_tf = float(new_val/(self.documents[doc_id][1]))
                            new_posting_name_dict[lower_term][doc_id] = "%.3f" % new_tf

                        if term in self.inverted_idx:
                            self.inverted_idx.pop(term)
                        term = lower_term


                    elif term not in new_posting_name_dict:
                            new_posting_name_dict[term] = posting_name_dict[term]

                    documents_posting_name_dict = new_posting_name_dict[term]
                    documents_posting_name_dict['idf'] = "%.3f" % (num_of_documents / self.inverted_idx[term])  # idf
                    if term not in merged_dict:
                        merged_dict[term] = {}
                    merged_dict[term].update(documents_posting_name_dict)

                new_posting_name_dict.clear()

            new_posting_name_dict.clear()
            merged_file = open(self.config + '\\' + posting_name + '.pkl', "wb")
            pickle.dump(merged_dict, merged_file)
            merged_file.close()
            merged_dict.clear()

        self.postingcounter.clear()

        docs_file = open(self.config + '\\documents.pkl', "wb")
        pickle.dump(self.documents, docs_file)
        docs_file.close()
        self.documents.clear()

        docs_file = open(self.config + '\\inverted_idx.pkl', "wb")
        pickle.dump(self.inverted_idx, docs_file)

        self.inverted_idx.clear()
        #self.postingcounter.clear()

        # self.mergeCommonFiles(common_count)

    def mergeCommonFiles(self, common_coumnt):

        common_name_dict = {}

        for i in range(common_coumnt):
            common_name_file = "common" + str(i)
            file_path = self.config + '\\' + common_name_file + '.pkl'
            temp_common_name_dict = {}
            with (open(file_path, "rb")) as openfile:
                while True:
                    try:
                        temp_common_name_dict = pickle.load(openfile)
                    except EOFError:
                        break
            try:
                os.remove(file_path)
            except:
                print("no such a file of name" + str(i))

            common_name_dict.update(temp_common_name_dict)

        f = open(self.config + '\\common.pkl', 'wb')
        pickle.dump(common_name_dict, f)
        f.close()


    def find_posting_files(self, posting_name):
            posting_lst = []
            num_of_posting = self.postingcounter[posting_name]
            for i in range(num_of_posting):
                file_path = self.config + '\\' + posting_name + str(i) + '.pkl'
                posting_lst.append(file_path)

            return posting_lst

    def find_common_terms(self):
        sorted_terms = sorted(self.inverted_idx, key=self.inverted_idx.get, reverse=True)
        first_20 = int(0.2 * len(sorted_terms))
        sorted_first_20 = sorted_terms[:first_20]
        sorted_terms_dict = {sorted_first_20[i]: 0 for i in range(0, len(sorted_first_20))}

        return sorted_terms_dict

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
            f = open(self.config + '\\' + posting_name + '.pkl', 'wb')
            pickle.dump(temp_term_dict, f)
            f.close()

        self.terms_idx.clear()
        self.postingDict.clear()

    # def add_the_rest_documents(self):
    #     for key in self.documents_idx:
    #         if (self.documents_idx[key] == {}):
    #             continue
    #         document_name = "document" + str(key)
    #         f = open(self.config + '\\' + document_name + '.pkl', 'ab')
    #         pickle.dump(self.documents_idx[key], f)
    #         f.close()
    #         self.documents_idx[key] = {}


    def uploadDocumentsFromPosting(self):

        for key in self.documents_idx:
            if self.documents_idx[key] != {}:
                self.documents.update(self.documents_idx[key])
                self.documents_idx[key] = {}

            for i in range(self.documentsCounter[key]):
                document_name = "doc" + self.numberToCharDict[key] + str(i)
                file_path = self.config + '\\' + document_name + '.pkl'
                documents_name_dict = {}
                with (open(file_path, "rb")) as openfile:
                    while True:
                        try:
                            documents_name_dict = pickle.load(openfile)
                        except EOFError:
                            break
                try:
                    os.remove(file_path)
                except:
                    print("no such a file of name" + str(key))

                self.documents.update(documents_name_dict)