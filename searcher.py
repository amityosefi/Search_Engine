import pickle

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

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """

        relevant_docs = []
        query_tokens = self.parser.parse_sentence(query)
        new_query_tokens = []
        for token in query_tokens:
            token = str(token)
            if token == token.lower():
                new_query_tokens.append(token)
            elif token.lower() in Parse.corpus_dict:
                new_query_tokens.append(token.lower())
            else:
                new_query_tokens.append(token)

        with open(self.path + '\\ldamodel.pkl', 'rb') as handle:
            lda_model = pickle.load(handle)

        with open(self.path + '\\ldadictionary.pkl', 'rb') as handle:
            dictionary = pickle.load(handle)

        query_tokens = new_query_tokens
        new_query_tokens.clear()
        new_bow = dictionary.doc2bow(query_tokens)
        topic_vector = lda_model.get_document_topics(bow=new_bow)
        print(topic_vector)

        mx = 0
        if len(topic_vector) > 1:
            for topic in topic_vector:
                if topic[1] > mx:
                    mx = topic[1]

        print("the prob of the query is: " +str(mx))

        # print(topic_vector)
        # topic_vector = self.lda.lda_model[self.bow_corpus[self.lda.counter]]

        try:  # an example of checks that you have to do
            with (open(self.path + '\\searcher.pkl', "rb")) as openfile:
                while True:
                    try:
                        dict = pickle.load(openfile)
                    except EOFError:
                        break
        except:
            print('term not found in posting')

        for topicID, prob in topic_vector:
            if prob > 0.6 or prob >= mx:
                for doc in dict[topicID]:
                    relevant_docs.append(doc[0])

        #print(len(relevant_docs))
        #print(relevant_docs)
        return relevant_docs, query_tokens

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