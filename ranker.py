import math
import pickle
from math import sqrt
import searcher


class Ranker:
    def __init__(self, output_path, stem):
        self.output_path = output_path
        self.terms_dict = {}
        self.documents = {}
        if stem:
            with open('inverted_idxwithstem.pkl', 'rb') as handle:
                self.inverted_idx = pickle.load(handle)
        else:
            with open('inverted_idxwithoutstem.pkl', 'rb') as handle:
                self.inverted_idx = pickle.load(handle)

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

    def rank_relevant_doc(self, relevant_doc, query_tokens, docslen):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param query_tokens:
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        documentsLen = docslen
        self.documents = relevant_doc

        query_tokens_dict = {query_tokens[i]: 0 for i in range(0, len(query_tokens))}
        cosSimilarity_list = []
        num_of_query_tokens = len(query_tokens_dict)

        for document in relevant_doc:
            sum_weights = 0
            num_of_same_tokens = 0
            total_squerded_weights = 0
            doc_terms_dict = self.documents[document][0] #documnts dictionary terms
            max_tf = self.documents[document][1] #max tf
            cosSimilarity_calculate = 0
            for term in doc_terms_dict:
                origin_term = term
                if not ('@' in term or '#' in term or '$' in term or '%' in term):
                    term = term.lower()
                x = float(documentsLen)
                y = float(self.inverted_idx[term][0])
                z = float(doc_terms_dict[origin_term])
                idf = float(math.log(float(documentsLen)/float(self.inverted_idx[term][0]), 2))
                tf = float(doc_terms_dict[origin_term])/float(max_tf)
                term_weight = tf * idf
                squared_weights = term_weight ** 2
                # if term in self.terms_dict:
                #     term_weight = float(self.terms_dict[term][document]) * float(self.terms_dict[term]['idf'])
                #     squared_weights = term_weight**2
                # else:
                #     try:
                #         posting_name = self.find_posting_name(term)
                #     except:
                #         continue
                #     additional_terms_dict = {}
                #     self.terms_dict.clear()
                #     with (open(self.output_path + '\\' + posting_name + '.pkl', "rb")) as openfile:
                #         additional_terms_dict = pickle.load(openfile)
                #
                #     term_weight = float(additional_terms_dict[term][document]) * float(additional_terms_dict[term]['idf'])
                #     squared_weights = term_weight**2
                # for word in additional_terms_dict:
                #     if word not in self.terms_dict:
                #         self.terms_dict[word] = additional_terms_dict[word]
                # self.terms_dict.update(additional_terms_dict)
                # additional_terms_dict.clear()
                if term in query_tokens_dict:
                    sum_weights += term_weight # *1 of query
                    num_of_same_tokens += 1
                total_squerded_weights += squared_weights
            if num_of_same_tokens != 0:
                # total_squerded_weights = (sqrt(total_squerded_weights)) * (sqrt(num_of_same_tokens))
                total_squerded_weights = sqrt(total_squerded_weights * num_of_query_tokens)
                cosSimilarity_calculate = float("%.5f" % (sum_weights / total_squerded_weights))
            else:
                cosSimilarity_calculate = 0

            cosSimilarity_list.append([document, cosSimilarity_calculate])

        # if len(self.terms_dict) >= 55000:
        # self.terms_dict.clear()

        cosSimilarity_list.sort(key=lambda x: float(x[1]), reverse= True)
        return cosSimilarity_list

        # return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)

    def retrieve_top_k(self, sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]