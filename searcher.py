import pickle

from parser_module import Parse
from ranker import Ranker
import utils


class Searcher:

    def __init__(self, parser, path):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = parser
        self.ranker = Ranker()
        self.path = path

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        # posting = utils.load_obj("posting.pkl")
        relevant_docs = {}
        for term in query:
            try: # an example of checks that you have to do
                posting_name = term[0]
                with (open(self.path + '\\' + posting_name + '.pkl', "rb")) as openfile:
                    while True:
                        try:
                            objects = pickle.load(openfile)
                        except EOFError:
                            break
                if term in objects:
                    for tweet in objects[term]:
                        # print(objects[term])
                        # print(tweet)
                        # print(tweet[0])
                        # print([tweet][1])
                        # print([tweet][2])

                        relevant_docs[tweet[0]] = [tweet[1], tweet[2]]

            except:
                print('term {} not found in posting'.format(term))

        f = open(self.path + '\\searcher.pkl', "wb")
        pickle.dump(relevant_docs, f)
        f.close()

        print(relevant_docs)
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
