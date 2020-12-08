import collections
import itertools
import math
import pickle
import os


class Indexer:

    def __init__(self, output_path,stem):
        self.stem = stem
        self.inverted_idx = {}  # key = term , value = count the documents that the term exist and how the term should appear
        self.terms_idx = {}  # key = char , value = terms
        self.postingDict = {}  # key = term, value = tf, idf
        # self.documents = {}
        self.config = output_path
        self.postingcounter = {}  # key = letters, value = count posting files from each letter
        # self.numberToCharDict = {'0': 'a', '1': 'b', '2': 'c', '3': 'd', '4': 'e', '5': 'f', '6': 'g', '7': 'h', '8': 'i', '9': 'j'}
        self.numOfDucuments = 0
        self.adddoc = []
        self.dictdoc = {}
        self.datacounter = 0
        # self.numofuploads=0
        self.uploadDocumentsCounter = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0}
        self.documents_idx = {'0': {}, '1': {}, '2': {}, '3': {}, '4': {}, '5': {}, '6': {}, '7': {}, '8': {}, '9': {}}
        self.documentsCounter = {'zero_documents': 0, 'first_documents':0,'second_documents':0,'third_documents':0, 'fourth_documents': 0, 'fifth_documents': 0,
                                'sixth_documents': 0, 'seventh_documents': 0, 'eighth_documents': 0, 'ninth_documens': 0}
        self.documentsFilesName = {'0': 'zero_documents', '1': 'first_documents', '2': 'second_documents', '3': 'third_documents', '4': 'fourth_documents',
                                   '5': 'fifth_documents', '6':'sixth_documents', '7': 'seventh_documents', '8': 'eighth_documents', '9': 'ninth_documens'}

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        print(self.numOfDucuments)

        doc_tokens = []
        for item in document.text_tokens:
            if not ('@' in item or '#' in item or '$' in item or '%' in item):
                item = item.lower()
            doc_tokens.append(item)

        if self.numOfDucuments % 50000 == 0 and self.numOfDucuments != 0:
            self.adddoc.append(doc_tokens)
            self.dictdoc[self.numOfDucuments] = document.tweet_id

            with open(self.config + '\\data' + str(self.datacounter) + '.pkl', 'wb') as f:
                pickle.dump(self.adddoc, f)
                self.adddoc.clear()
            self.datacounter += 1
        else:
            self.adddoc.append(doc_tokens)
            self.dictdoc[self.numOfDucuments] = document.tweet_id

        document_dictionary = document.term_doc_dictionary
        document_name = document.tweet_id[len(document.tweet_id) - 1]

        self.documents_idx[document_name][document.tweet_id] = [document_dictionary, document.max_tf]
        self.documentsCounter[self.documentsFilesName[document_name]] += 1
        if (self.documentsCounter[self.documentsFilesName[document_name]] % 55000 == 0):
            self.uploadDocumnetToPostingFile(document_name)

        self.numOfDucuments += 1

        # Go over each term in the doc
        for term in document_dictionary:
            try:
                # if term == '' or str(term).isspace():
                #     continue
                origin_term = term

                if ('@' in term or '#' in term or '$' in term or '%' in term):
                    if term not in self.inverted_idx:
                        self.inverted_idx[term] = [1, term]  # [0]:count documents of the term   [1]:idf
                    else:
                        self.inverted_idx[term][0] += 1  # there key already in the dict
                else:
                    if term.lower() not in self.inverted_idx:
                        if term[0] == term[0].lower():
                            self.inverted_idx[term.lower()] = [1, term.lower()]  # [0]:count documents of the term   [1]:idf
                        else:
                            self.inverted_idx[term.lower()] = [1, term.upper()]
                    elif term[0] == term[0].lower():
                        self.inverted_idx[term.lower()][1] = term.lower()
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
                    # print( "%.5f" % float(document_dictionary[origin_term]))
                    # print(document.max_tf)
                    self.postingDict[term][document.tweet_id] = "%.5f" % float(
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
                continue


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

    def uploadDocumnetToPostingFile(self, name):
        with open(self.config + '\\' + self.documentsFilesName[name] + str(self.uploadDocumentsCounter[name]) + '.pkl', 'wb') as f:
            pickle.dump(self.documents_idx[name], f)

        self.documents_idx[name].clear()
        self.uploadDocumentsCounter[name] += 1


    def uploadTokensToPostingFile(self, term_lst, c):

        posting_name = c + str(self.postingcounter[c])
        temp_term_dict = {}
        for term in term_lst:
            temp_term_dict[term] = self.postingDict[term]
            self.postingDict.pop(term)

        f = open(self.config + '\\' + posting_name + '.pkl', 'wb')
        pickle.dump(temp_term_dict, f)
        f.close()

    def merge_posting_files(self):

        if self.stem:
            docs_file = open('inverted_idxwithstem.pkl', "wb")
            pickle.dump(self.inverted_idx, docs_file)
        else:
            docs_file = open('inverted_idxwithoutstem.pkl', "wb")
            pickle.dump(self.inverted_idx, docs_file)

        self.inverted_idx.clear()

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
                with (open(posting_file, "rb")) as openfile:
                    posting_name_dict = pickle.load(openfile)
                os.remove(posting_file)

                for term in posting_name_dict:
                    if term not in merged_dict:
                        merged_dict[term] = posting_name_dict[term]
                    else:
                        for item in posting_name_dict[term]:
                            if item not in merged_dict[term]:
                                merged_dict[term][item] = posting_name_dict[term][item]

            for term in merged_dict:
                documents_posting_name_dict = merged_dict[term]
                num_documents_of_term = len(documents_posting_name_dict)
                documents_posting_name_dict['idf'] = "%.3f" % math.log((self.numOfDucuments / num_documents_of_term), 2)  # idf
                merged_dict[term] = documents_posting_name_dict

            with open(self.config + '\\' + posting_name + '.pkl', "wb") as merged_file:
                pickle.dump(merged_dict, merged_file)
            merged_dict.clear()

        self.postingcounter.clear()

        with open(self.config + '\\data' + str(self.datacounter) + '.pkl', 'wb') as f:
            pickle.dump(self.adddoc, f)
            self.datacounter += 1
        self.adddoc.clear()

        self.mergeDocumentsFromPosting()


    def find_posting_files(self, posting_name):
        posting_lst = []
        num_of_posting = self.postingcounter[posting_name]
        for i in range(num_of_posting):
            file_path = self.config + '\\' + posting_name + str(i) + '.pkl'
            posting_lst.append(file_path)

        return posting_lst

    def mergedoctype(self, name, number):

        file_list=[]
        for i in range(number):
            file_list.append(self.config + '\\' + name + str(i) + '.pkl')

        tmp_dict = {}
        for file in file_list:
            with (open(file, "rb")) as openfile:
                posting_dict = pickle.load(openfile)
            os.remove(file)

            for k in posting_dict:
                tmp_dict[k] = posting_dict[k]

        conunt = len(tmp_dict)
        with open(self.config + '\\' + name + '.pkl', "wb") as f:
            pickle.dump(tmp_dict, f)

        return conunt

    def mergeDocumentsFromPosting(self):

        for i in range(len(self.documents_idx)):
            name = str(i)
            if self.documents_idx[name] != {}:
                self.uploadDocumnetToPostingFile(name)
        j = 0
        count = 0
        for key in self.documentsCounter:
            count += self.mergedoctype(key, self.uploadDocumentsCounter[str(j)])
            j += 1

        # print("num of documents is  " + str(count))
