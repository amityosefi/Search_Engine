import pickle

from parser_module import Parse
from ranker import Ranker
import utils
import gensim.corpora.dictionary


class Searcher:

    def __init__(self, parser, path, lda):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = parser
        self.ranker = Ranker()
        self.path = path
        self.lda = lda

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        # posting = utils.load_obj("posting.pkl")
        print("start searcher")

        try:  # an example of checks that you have to do
            with (open(self.path + '\\searcher.pkl', "rb")) as openfile:
                while True:
                    try:
                        objects = pickle.load(openfile)
                    except EOFError:
                        break
        except:
            print('term not found in posting')

        relevant_docs = {}

        query = self.parser.parse_sentence(query)
        new_bow = self.lda.dictionary.doc2bow(query)
        topic_vector = self.lda.lda_model.get_document_topics(bow=new_bow)
        mx = 0
        if len(topic_vector) > 1:
            for topic in topic_vector:
                if topic[1] > mx:
                    mx = topic[1]
        # print(topic_vector)
        # topic_vector = self.lda.lda_model[self.bow_corpus[self.lda.counter]]
        for topicID, prob in topic_vector:
            if prob > 0.6 or prob >= mx:
                for doc in objects[topicID]:
                    relevant_docs[doc[0]] = ''
        print(len(relevant_docs))
        return relevant_docs

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
