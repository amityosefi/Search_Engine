import pickle

import LDAModel
from parser_module import Parse
from ranker import Ranker
from parser_module import Parse
import utils
import gensim.corpora.dictionary


class Searcher:

    def __init__(self, parser, output_path):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = parser
        self.ranker = Ranker(output_path)
        self.path = output_path
        self.counter = 1
        self.inverted_idx = utils.load_inverted_index(output_path)
        with open(self.path + '\\ldamodelpickle.pkl', 'rb') as handle:
            self.lda_model = pickle.load(handle)

        with open(self.path + '\\ldadictionary.pkl', 'rb') as handle:
            self.dictionary = pickle.load(handle)

        with open(self.path + '\\searcher.pkl', 'rb') as handle:
            self.dict = pickle.load(handle)

        with open(self.path + '\\documents.pkl', 'rb') as handle:
            self.documents = pickle.load(handle)

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """

        relevant_docs = []
        self.parser.text_tokens = []
        query_tokens = self.parser.parse_sentence(query)
        new_query_tokens = []
        for token in query_tokens:
            if not ('@' in token or '#' in token or '$' in token or '%' in token):
                token = token.lower()
            new_query_tokens.append(token)



        # lda_model = LDAModel.lda_model
        dictquery = {new_query_tokens[i]: 0 for i in range(0, len(new_query_tokens))}
        new_bow = self.dictionary.doc2bow(new_query_tokens)
        topic_vector = self.lda_model.get_document_topics(bow=new_bow)

        mx = 0
        if len(topic_vector) > 1:
            for topic in topic_vector:
                if topic[1] > mx:
                    mx = topic[1]

        print("the prob of the query is: " + str(mx))

        # print(topic_vector)
        # topic_vector = self.lda.lda_model[self.bow_corpus[self.lda.counter]]


        for topicID, prob in topic_vector:
            if prob > 0.6 or prob >= mx:
                if topicID not in self.dict:
                    continue
                for doc in list(self.dict[topicID]):
                    for term in self.documents[doc[0]][0]:
                        if not ('@' in term or '#' in term or '$' in term or '%' in term):
                            term = term.lower()
                        if term in dictquery:
                            relevant_docs.append(doc[0])
                            break

        #print(len(relevant_docs))
        #print(relevant_docs)
        return relevant_docs, new_query_tokens

        # posting = utils.load_obj("posting")
        # relevant_docs = {}
        # for term in query:
        #     try: # an example of checks that you have to do
        #         posting_doc = posting[term]
        #         for doc_tuple in posting_doc:
        #             doc = doc_tuple[0]
        #             if doc not in relevant_docs.keys():
        #                 relevant_docs[doc] = 1
        #             else:
        #                 relevant_docs[doc] += 1
        #     except:
        #         print('term {} not found in posting'.format(term))
        # return relevant_docs