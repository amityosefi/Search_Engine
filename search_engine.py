import time

from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
import utils
import os

from searcher import Searcher


def run_engine():
    """
    :return:
    """

    number_of_documents = 0

    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()
    indexer = Indexer(corpus_path=config.get_savedFileMainFolder())

    start_reader = time.time()
    documents_list = r.read_dir()
    end_reader = time.time() - start_reader
    print("Reader takes:" + str(end_reader) + "seconds")

    start_parsing = time.time()
    # Iterate over every document in the file
    for idx, document in enumerate(documents_list):
        print(number_of_documents)
        number_of_documents += 1

        # parse the document
        parsed_document = p.parse_doc(document)

        # index the document data
        indexer.add_new_doc(parsed_document)

    end_parsing = time.time() - start_parsing
    print("parser and indexing takes:" + str(end_parsing) + "seconds")
    print('Finished parsing and indexing. Starting to export files')

    utils.save_obj(indexer.inverted_idx, "inverted_idx")
    # utils.save_obj(indexer.postingDict, "posting")


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


def search_and_rank_query(query, inverted_index, k):
    p = Parse()
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)



def main():
    run_engine()


    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    for doc_tuple in search_and_rank_query(query, inverted_index, 2000):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))