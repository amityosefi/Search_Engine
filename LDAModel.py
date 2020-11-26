import pickle
import time
import gensim
from smart_open import open


class LDA:

    counter = 0

    def __init__(self):
        self.dictionary = gensim.corpora.Dictionary([])
        self.bow_corpus = [self.dictionary.doc2bow(doc) for doc in []]
        self.lda_model = None
        self.docs = {}

    def addDoc(self, document):
       # for line in open(file):
            # assume there's one document per line, tokens separated by whitespace
        #    yield self.dictionary.doc2bow(line)
        self.dictionary.add_documents([document.text_tokens])
        self.bow_corpus.append(self.dictionary.doc2bow(document.text_tokens, allow_update=True))
        self.docs[self.counter] = document.tweet_id
        self.counter += 1

    def initialModel(self, path):
        print("start load the LDA modle")
        start = time.time()
        self.lda_model = gensim.models.LdaMulticore(self.bow_corpus, 50, self.dictionary)

        end = time.time() - start
        print("end load the LDA modle in: " + str(end) + " sec")


        # for i in range(5):
        #     print(self.lda_model.show_topic(i))
        # i = 0
        # for i in range(8):
        #     for index, score in sorted(self.lda_model[self.bow_corpus[i]], key=lambda tup: -1 * tup[1]):
        #         print("\nScore: {}\t \nTopic: {}".format(score, self.lda_model.print_topic(index, 10)))
        #     print(i)
        #     i += 1

        topic_dict = {}
        j=0
        for docID in range(self.counter):
            topic_vector = self.lda_model[self.bow_corpus[docID]]
            print(j)
            j+=1
            for topicID, prob in topic_vector:
                if prob > 0.9:
                    if topicID in topic_dict:
                        topic_dict[topicID].append([self.docs[docID],prob])
                    else:
                        topic_dict[topicID] = [[self.docs[docID],prob]]

        f = open(path + '\\searcher.pkl', "wb")
        pickle.dump(topic_dict, f)
        f.close()

        print("topic 0 with :" + str(len(topic_dict[0])) + " docs")
        print("topic 1 with :" + str(len(topic_dict[1])) + " docs")
        print("topic 2 with :" + str(len(topic_dict[2])) + " docs")



        topic_dict.clear()