import time

from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
import utils
import os

from searcher import Searcher


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
    print("Reader takes:" + str(end_reader) + "seconds")

    start_parsing = time.time()
    # Iterate over every document in the file
    for idx, document in enumerate(documents_list):
        print(number_of_documents)
        number_of_documents += 1

        # parse the document
        parsed_document = p.parse_doc(document)
        # parsed_document = p.parse_doc(documents_list[32841])

        # index the document data
        indexer.add_new_doc(parsed_document)

    end_parsing = time.time() - start_parsing
    print("parser and indexing takes:" + str(end_parsing) + "seconds")
    print('Finished parsing and indexing. Starting to export files')

    indexer.merge_posting_files()

    utils.save_obj(indexer.inverted_idx, output_path + "\\inverted_idx")
    utils.save_obj(indexer.postingDict, output_path + "\\posting")


def load_index(output_path):
    print('Load inverted index')
    inverted_index = utils.load_obj(output_path + "\\inverted_idx")
    return inverted_index


def search_and_rank_query(queries, inverted_index, num_docs_to_retrieve, stemming,output_path):

    pa = Parse(stemming)
    if isinstance(queries, list):
        for query in queries:
            check_query(query, inverted_index, num_docs_to_retrieve, pa,output_path)
    else:
        try:
            f = open(queries, "r")
            for query in f:
                print(query)
                check_query(query, inverted_index, num_docs_to_retrieve,pa,output_path)
            f.close()
        except:
            print("not working")

def check_query(query,inverted_index, num_docs_to_retrieve, p,output_path):
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index, p, output_path)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, num_docs_to_retrieve)


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve=2000):
    # f = open(queries, "r")
    # while True:
    #     if not f.readline():
    #         break
    #     print(f.readline())

    run_engine(corpus_path, output_path, stemming)

    inverted_index = load_index(output_path)

    for doc_tuple in search_and_rank_query(queries, inverted_index, num_docs_to_retrieve, stemming,output_path):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
