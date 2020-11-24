import gensim as gensim
from sklearn.decomposition import LatentDirichletAllocation as LDA

class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_doc(relevant_doc):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=id2word,
                                                    num_topics=20,
                                                    random_state=100,
                                                    update_every=1,
                                                    chunksize=100,
                                                    passes=10,
                                                    alpha='auto',
                                                    per_word_topics=True)



        return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)

    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k=2000):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]
