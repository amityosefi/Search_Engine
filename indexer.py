import collections
import itertools
import pickle
import os


class Indexer:

    def __init__(self, output_path):
        # self.inverted_idx = {}  # key = term , value = count the documents that the term exist
        self.terms_idx = {}  # key = char , value = terms
        self.postingDict = {}  # key = term, value = tf, idf
        self.config = output_path
        self.postingcounter = {}  # key = letters, value = count posting files from each letter
        self.documents_idx = {}  # key = last digit of each tweet id, key = dict of documents with the same digit
        self.documentsCounter = {}  # key = numbers of docs, value = count posting files from each doc
        self.documents = {}  # key = tweet id , value = term dict, max_tf, num of unique words
        # self.doc_counter = 0
        self.count = 0
        self.inverted_idx = {}
        self.adddoc = []
        self.counterdoc = 0
        self.counter = 0
        self.dictdoc = {}
        self.datacounter = 0

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        print(self.count)
        self.count += 1
        doc_tokens = []
        for item in document.text_tokens:
            if not (item[0] == '@' or item[0] == '#' or item[0] == '%' or item[0] == '$' or '0' <= item[0] <= '9'):
                item = item.lower()
            doc_tokens.append(item)

        if self.count % 10000 == 0 and self.count != 0:
            self.adddoc.append(doc_tokens)
            self.dictdoc[self.counterdoc] = document.tweet_id

            with open(self.config + '\\data' + str(self.datacounter) + '.pkl', 'wb') as f:
                pickle.dump(self.adddoc, f)
                self.adddoc.clear()
            self.counterdoc += 1
            self.datacounter += 1
        else:
            self.adddoc.append(doc_tokens)
            self.dictdoc[self.counterdoc] = document.tweet_id
            self.counterdoc += 1

        document_dictionary = document.term_doc_dictionary
        documentsTempDict = {}
        documentsTempDict[document.tweet_id] = [document_dictionary, document.max_tf, document.num_of_unique_words]
        document_name = document.tweet_id[len(document.tweet_id) - 1]
        if document_name not in self.documents_idx:
            self.documents_idx[document_name] = {}
        self.documents_idx[document_name].update(documentsTempDict)
        if document_name not in self.documentsCounter:
            self.documentsCounter[document_name] = 0
        if len(self.documents_idx[document_name]) == 100000:
            self.uploadDocumnetToPostingFile(document_name)
            self.documentsCounter[document_name] += 1

        # self.doc_counter += 1
        # self.lda.addDoc(document)

        # Go over each term in the doc
        for term in document_dictionary:
            try:
                # if term == '' or str(term).isspace():
                #     continue
                origin_term = term

                if (term[0] == '@' or term[0] == '#' or term[0] == '$' or term[0] == '%' or '0' <= term[0] <= '9'):
                    if term not in self.inverted_idx:
                        self.inverted_idx[term] = [1, 0, 0]  # [0]:count documents of the term   [1]:idf
                    else:
                        self.inverted_idx[term][0] += 1  # ther key already in the dict

                else:
                    if term.lower() not in self.inverted_idx:
                        if term[0] == term[0].lower():
                            self.inverted_idx[term.lower()] = [1, 0,term.lower()]  # [0]:count documents of the term   [1]:idf
                        else:
                            self.inverted_idx[term.lower()] = [1, 0, term.Upper()]
                    elif term[0] == term[0].lower():
                        self.inverted_idx[term.lower()][2] = term.lower()
                        self.inverted_idx[term.lower()][0] += 1  # ther key already in the dict
                    else:
                        self.inverted_idx[term.lower()][0] += 1
                    term = term.lower()



                posting_name = self.find_posting_name(term)

                if posting_name not in self.terms_idx:
                    self.terms_idx[posting_name] = []

                self.terms_idx[posting_name].append(term)

                if term not in self.postingDict:
                    self.postingDict[term] = {}

                if document.doc_length > 0:
                    self.postingDict[term][document.tweet_id] = "%.3f" % float(
                        document_dictionary[origin_term] / document.max_tf)  # tf
                else:
                    self.postingDict[term][document.tweet_id] = 0.9  # tf

                if posting_name not in self.postingcounter:
                    self.postingcounter[posting_name] = 0

                if len(self.terms_idx[posting_name]) == 150000:
                    # sorted_term_lst = sorted(self.terms_idx[posting_name])
                    term_lst = list(dict.fromkeys(self.terms_idx[posting_name]))  # remove duplicates
                    self.terms_idx[posting_name] = []
                    self.uploadTokensToPostingFile(term_lst, posting_name)
                    self.postingcounter[posting_name] += 1
                    # self.printPostingFile('documents')

            except:
                print('problem with the following key {}'.format(term))

    def findFirstChar(self, term):

        firstChar = term[0].lower()
        i = 0
        while not ('a' <= firstChar <= 'z'):
            """
            if i == len(term) - 1:
                if not ('a' <= posting_name <= 'z' or 'A' <= posting_name <= 'Z' or '0' <= posting_name <= '9' or posting_name == '$'):
                    flag = True
                    break
            """

            i += 1
            firstChar = str(term[i]).lower()

        return firstChar

    def find_posting_name(self, term):

        term = str(term)

        if '$' in term or '%' in term:
            posting_name = 'delimiters'
        else:
            posting_name = term[0].lower()
            i = 0
            while not ('a' <= posting_name <= 'z' or '0' <= posting_name <= '9' or posting_name == '$'):
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

        num_of_documents = len(self.documents_idx)
        self.mergeDocumentsFromPosting()

        merged_dict = {}

        for posting_name in self.postingcounter:
            posting_name_dict = {}

            if self.terms_idx[posting_name] != []:
                term_lst = list(dict.fromkeys(self.terms_idx[posting_name]))
                for term in term_lst:
                    posting_name_dict[term] = self.postingDict[term]
                    self.postingDict.pop(term)
                self.terms_idx[posting_name] = []

            for term in posting_name_dict:
                if term not in merged_dict:
                    merged_dict[term] = posting_name_dict[term]
                else:
                    for item in posting_name_dict[term]:
                        if item not in merged_dict[term]:
                            merged_dict[term][item] = posting_name_dict[term][item]

            posting_lst = self.find_posting_files(posting_name)
            for posting_file in posting_lst:
                try:
                    with (open(posting_file, "rb")) as openfile:  # 5555555555555555555555555555555555555555
                        posting_name_dict = pickle.load(openfile)
                    os.remove(posting_file)
                except:
                    print("no such a file of name" + str(posting_name))

                for term in posting_name_dict:
                    if term not in merged_dict:
                        merged_dict[term] = posting_name_dict[term]
                    else:
                        for item in posting_name_dict[term]:
                            if item not in merged_dict[term]:
                                merged_dict[term][item] = posting_name_dict[term][item]

            for term in merged_dict:
                documents_posting_name_dict = merged_dict[term]
                documents_posting_name_dict['idf'] = "%.3f" % (num_of_documents / self.inverted_idx[term][0])  # idf
                merged_dict[term] = documents_posting_name_dict

            merged_file = open(self.config + '\\' + posting_name + '.pkl', "wb")
            pickle.dump(merged_dict, merged_file)
            merged_file.close()
            merged_dict.clear()

        self.postingcounter.clear()

        docs_file = open(self.config + '\\inverted_idx.pkl', "wb")
        pickle.dump(self.inverted_idx, docs_file)
        self.inverted_idx.clear()

        lst = []
        for i in range(self.datacounter):
            with open(self.config + '\\data' + str(i) + '.pkl', 'rb') as handle:
                self.adddoc += pickle.load(handle)
            os.remove(self.config + '\\data' + str(i) + '.pkl')
        lst += self.adddoc
        self.adddoc.clear()
        with open(self.config + '\\data.pkl', 'wb') as f:
            pickle.dump(lst, f)

        # self.mergeCommonFiles(common_count)

    def find_posting_files(self, posting_name):
        posting_lst = []
        num_of_posting = self.postingcounter[posting_name]
        for i in range(num_of_posting):
            file_path = self.config + '\\' + posting_name + str(i) + '.pkl'
            posting_lst.append(file_path)

        return posting_lst

    def mergeDocumentsFromPosting(self):

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

        docs_file = open(self.config + '\\documents.pkl', "wb")
        pickle.dump(self.documents, docs_file)
        docs_file.close()
        self.documents.clear()

    # def mergeCommonFiles(self, common_coumnt):
    #
    #     common_name_dict = {}
    #
    #     for i in range(common_coumnt):
    #         common_name_file = "common" + str(i)
    #         file_path = self.config + '\\' + common_name_file + '.pkl'
    #         temp_common_name_dict = {}
    #         with (open(file_path, "rb")) as openfile:
    #             while True:
    #                 try:
    #                     temp_common_name_dict = pickle.load(openfile)
    #                 except EOFError:
    #                     break
    #         try:
    #             os.remove(file_path)
    #         except:
    #             print("no such a file of name" + str(i))
    #
    #         common_name_dict.update(temp_common_name_dict)
    #
    #     f = open(self.config + '\\common.pkl', 'wb')
    #     pickle.dump(common_name_dict, f)
    #     f.close()

    # def find_common_terms(self):
    #     sorted_terms = sorted(self.inverted_idx, key=self.inverted_idx.get, reverse=True)
    #     first_20 = int(0.2 * len(sorted_terms))
    #     sorted_first_20 = sorted_terms[:first_20]
    #     sorted_terms_dict = {sorted_first_20[i]: 0 for i in range(0, len(sorted_first_20))}
    #
    #     return sorted_terms_dict

    # def add_the_rest_terms(self):
    #     for key in self.terms_idx:
    #         if (self.terms_idx[key] == []):
    #             continue
    #         term_lst = list(dict.fromkeys(self.terms_idx[key]))
    #         temp_term_dict = {}
    #         for term in term_lst:
    #             temp_term_dict[term] = self.postingDict[term]
    #             self.postingDict.pop(term)
    #         posting_name = key + str(self.postingcounter[key])
    #         f = open(self.config + '\\' + posting_name + '.pkl', 'wb')
    #         pickle.dump(temp_term_dict, f)
    #         f.close()
    #
    #     self.terms_idx.clear()
    #     self.postingDict.clear()

    # def add_the_rest_documents(self):
    #     for key in self.documents_idx:
    #         if (self.documents_idx[key] == {}):
    #             continue
    #         document_name = "document" + str(key)
    #         f = open(self.config + '\\' + document_name + '.pkl', 'ab')
    #         pickle.dump(self.documents_idx[key], f)
    #         f.close()
    #         self.documents_idx[key] = {}
