import pickle
from math import sqrt


class Ranker:
    def __init__(self, output_path):
        self.output_path = output_path
        self.terms_dict = {}
        self.documents = {}
        self.common = {}

    def load_docs_and_terms(self):

        with (open(self.output_path + '\\documents.pkl', "rb")) as openfile:
            while True:
                try:
                    self.documents = pickle.load(openfile)
                except EOFError:
                    break

        with (open(self.output_path + '\\common.pkl', "rb")) as openfile:
            while True:
                try:
                    self.common = pickle.load(openfile)
                except EOFError:
                    break
        self.terms_dict.update(self.common)


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

    def rank_relevant_doc(self, relevant_doc, query_tokens):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param query_tokens:
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """

        query_tokens_dict = {query_tokens[i]: 0 for i in range(0, len(query_tokens))}


        # self.documents[document.tweet_id] = [document.max_tf, document.num_of_unique_words, document_dictionary]
        # self.postingDict[term].append([document.tweet_id, document_dictionary[term],
        #                                "%.3f" % float(document_dictionary[term] / document.max_tf), (num_of_documents / self.inverted_idx[term])])  # tf

        cosSimilarity_dict = {}
        num_of_query_tokens = len(query_tokens_dict)

        for document in relevant_doc:
            sum_weights = 0
            sum_of_squared_weights = 0
            num_of_same_tokens = num_of_query_tokens
            document = str(document)
            doc_terms_dict = self.documents[document][0]
            for term in doc_terms_dict:
                term = str(term)
                if term not in query_tokens_dict:
                    num_of_same_tokens -= 1
                    if num_of_same_tokens == 0:
                        break
                elif term in self.terms_dict:
                    term_weight = (float(self.terms_dict[term][document]) * float(self.terms_dict[term]['idf']))
                    sum_weights += term_weight  # *1 of query
                    sum_of_squared_weights += pow(term_weight, 2)
                # elif term.lower() in self.terms_dict:
                #     term = term.lower()
                #     term_weight = (float(self.terms_dict[term][document]) * float(self.terms_dict[term]['idf']))
                #     sum_weights += term_weight  # *1 of query
                #     sum_of_squared_weights += pow(term_weight, 2)
                else:
                    posting_name = self.find_posting_name(term)
                    with (open(self.output_path + '\\' + posting_name + '.pkl', "rb")) as openfile:
                        while True:
                            try:
                                additional_terms_dict = pickle.load(openfile)
                            except EOFError:
                                break
                    # if term.lower() in additional_terms_dict:
                    #     term = term.lower()
                    term_weight = float(additional_terms_dict[term][document]) * float(additional_terms_dict[term]['idf'])
                    sum_weights += term_weight  # *1 of query
                    sum_of_squared_weights += pow(term_weight, 2)
                    self.terms_dict.update(additional_terms_dict)
            if sum_weights != 0:
                cosSimilarity_calculate = sum_weights / (sqrt(sum_of_squared_weights))
            else:
                cosSimilarity_calculate = 0
            cosSimilarity_dict[document] = cosSimilarity_calculate


        sorted_relevant_docs = sorted(cosSimilarity_dict, key=cosSimilarity_dict.get, reverse=True)
        sort = sorted_relevant_docs[:20]
        for doc in sort:
            print(doc + "with rank of" + str(cosSimilarity_dict[doc]))
        print()
        return sorted_relevant_docs

        # return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)

    def retrieve_top_k(self, sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]