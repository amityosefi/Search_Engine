import pickle
from ranker import Ranker


class Searcher:

    def __init__(self, parser, output_path, stem):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = parser
        self.ranker = Ranker(output_path, stem)
        self.path = output_path
        self.counter = 1
        self.stem = stem
        self.lda_model = None
        self.dictionary = None
        self.dict = None
        self.documents = None
        self.docslen = 0
        self.documentfilenames = {'zero_documents': 0 , 'first_documents': 0, 'second_documents': 0, 'third_documents': 0,
                                  'fourth_documents': 0, 'fifth_documents': 0,
                                  'sixth_documents': 0, 'seventh_documents': 0, 'eighth_documents': 0,
                                  'ninth_documens': 0}


    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """

        relevant_docs = {}
        self.parser.text_tokens = []
        query_tokens = self.parser.parse_sentence(query)
        new_query_tokens = []
        for token in query_tokens:
            if not ('@' in token or '#' in token or '$' in token or '%' in token):
                token = token.lower()
            new_query_tokens.append(token)

        if self.stem:
            with open('ldamodelwithstem.pkl', 'rb') as handle:
                self.lda_model = pickle.load(handle)

            with open('ldadictionarywithstem.pkl', 'rb') as handle:
                self.dictionary = pickle.load(handle)

        else:
            with open('ldamodelwithoutstem.pkl', 'rb') as handle:
                self.lda_model = pickle.load(handle)

            with open('ldadictionarywithoutstem.pkl', 'rb') as handle:
                self.dictionary = pickle.load(handle)

        # lda_model = LDAModel.lda_model
        dictquery = {new_query_tokens[i]: 0 for i in range(0, len(new_query_tokens))}
        new_bow = self.dictionary.doc2bow(new_query_tokens)
        topic_vector = self.lda_model.get_document_topics(bow=new_bow)
        self.lda_model = None
        self.dictionary = None
        best_topic = 0
        mx = 0
        if len(topic_vector) > 1:
            for topic in topic_vector:
                if topic[1] > mx:
                    mx = topic[1]
                    best_topic = topic[0]

        # print("the prob of the query is: " + str(mx))
        with (open('ldasearcherwithstem.pkl', "rb")) as openfile:
            self.dict = pickle.load(openfile)

        for key in self.documentfilenames:
            with (open(self.path + '\\' + key + '.pkl', "rb")) as openfile:
                self.documents = pickle.load(openfile)
            self.docslen += len(self.documents)

            relevant_docs.update(self.find_relevant_docs_from_topics(topic_vector, dictquery, mx))

        self.documents.clear()
        self.dict.clear()
        return relevant_docs, new_query_tokens, self.docslen

    def find_relevant_docs_from_topics(self, topic_vector, dictquery, mx):
        tmp_relevant_docs = {}
        for topicID, prob in topic_vector:
            if prob > 0.4 or prob >= mx:
                if topicID not in self.dict:
                    continue
                for doc in list(self.dict[topicID]):
                    if doc[0] in self.documents:
                        for term in self.documents[doc[0]][0]:
                            if not ('@' in term or '#' in term or '$' in term or '%' in term):
                                term = term.lower()
                            if term in dictquery:
                                # relevant_docs.append(doc[0])
                                tmp_relevant_docs[doc[0]] = [self.documents[doc[0]][0], self.documents[doc[0]][1]]
                                break

        return tmp_relevant_docs
