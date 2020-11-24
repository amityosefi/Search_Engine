import time

from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
import utils
import os


def run_engine(corpus_path, output_path, stemming=False):
    """
    :return:
    """

    number_of_documents = 0

    config = ConfigClass(corpus_path, output_path, stemming)
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse(stemming)
    indexer = Indexer(corpus_path=config.get_savedFileMainFolder())

    start_reader = time.time()
    documents_list = r.read_dir()
    end_reader = time.time() - start_reader
    print("Reader takes" + str(end_reader) + "seconds")

    start_parsing = time.time()
    # Iterate over every document in the file
    for idx, document in enumerate(documents_list):
        # parse the document
        print(number_of_documents)
        parsed_document = p.parse_doc(document)
        number_of_documents += 1
   ## end_parsing = time.time() - start_parsing
    ##print(end_parsing)
    ##print("Parser takes" + str(end_parsing) + "seconds")

        # index the document data
        indexer.add_new_doc(parsed_document)
    end_parsing = time.time() - start_parsing
    print('Finished parsing and indexing. Starting to export files')

    indexer.merge_posting_files()

    utils.save_obj(indexer.inverted_idx, "inverted_idx")
    utils.save_obj(indexer.postingDict, "posting")

    print('finishing parsing and indexing takes' + str(end_parsing))

"""
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
"""


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve = 2000):
    run_engine(corpus_path, output_path, stemming)


    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    ##inverted_index = load_index()
    ##for doc_tuple in search_and_rank_query(query, inverted_index, k):
    ##  print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
    # inverted_index = load_index()
    # for doc_tuple in search_and_rank_query(queries, inverted_index, num_docs_to_retrieve):
    #     print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))