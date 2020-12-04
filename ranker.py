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

        # with (open(self.output_path + '\\common.pkl', "rb")) as openfile:
        #     while True:
        #         try:
        #             self.common = pickle.load(openfile)
        #         except EOFError:
        #             break
        # self.terms_dict.update(self.common)


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

        cosSimilarity_list = []
        #num_of_query_tokens = len(query_tokens_dict)

        for document in relevant_doc:
            sum_weights = 0
            num_of_same_tokens = 0
            total_squerded_weights = 0
            doc_terms_dict = self.documents[document][0]
            for term in doc_terms_dict:
                if not (term[0] == '@' or term[0] == '#' or term[0] == '%' or term[0] == '$' or '0' <= term[0] <= '9'):
                    term = term.lower()
                if term in self.terms_dict:
                    term_weight = (float(self.terms_dict[term][document]) * float(self.terms_dict[term]['idf']))
                    squared_weights = pow(2, term_weight)
                else:
                    posting_name = self.find_posting_name(term)
                    with (open(self.output_path + '\\' + posting_name + '.pkl', "rb")) as openfile:
                        while True:
                            try:
                                additional_terms_dict = pickle.load(openfile)
                            except EOFError:
                                break
                    term_weight = float(additional_terms_dict[term][document]) * float(additional_terms_dict[term]['idf'])
                    squared_weights = pow(2, term_weight)
                    self.terms_dict.update(additional_terms_dict)
                if term in query_tokens_dict:
                    sum_weights += term_weight # *1 of query
                    num_of_same_tokens += 1
                total_squerded_weights += squared_weights
            if num_of_same_tokens != 0:
                # total_squerded_weights = (sqrt(total_squerded_weights)) * (sqrt(num_of_same_tokens))
                total_squerded_weights = sqrt(total_squerded_weights * num_of_same_tokens)
                cosSimilarity_calculate = float("%.5f" % (sum_weights / total_squerded_weights))
            else:
                cosSimilarity_calculate = 0
            cosSimilarity_list.append([document, cosSimilarity_calculate])


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