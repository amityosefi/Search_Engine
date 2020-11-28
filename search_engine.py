import csv
import time
from LDAModel import LDA
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from smart_open import open
import utils
import os

from searcher import Searcher


def run_engine(corpus_path, output_path, stemming=False):
    """
    :return:
    """
    st = time.time()
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
    # documents_list = documents_list[:500]
    for idx, document in enumerate(documents_list):
        # if number_of_documents % 10000 == 0:
        print(number_of_documents)
        number_of_documents += 1

        # parse the document
        parsed_document = p.parse_doc(document)
        # parsed_document = p.parse_doc(documents_list[32841])

        # index the document data
        indexer.add_new_doc(parsed_document)
    print("the number of documents in the reader: " + str(number_of_documents))
    end_parsing = time.time() - start_parsing
    print("parser and indexing takes:" + str(end_parsing) + " seconds")
    # print('Finished parsing and indexing. Starting to export files')

    start_mege = time.time()
    indexer.merge_posting_files()
    end_merge = time.time() - start_mege
    print("the time takes to merge is: " + str(end_merge) + " sec")

    en = time.time()-st
    print("the time takes the hole reader parser and indexer after merge files are: " + str(en) + " sec")
    # utils.save_obj(indexer.inverted_idx, output_path + "\\inverted_idx")
    # utils.save_obj(indexer.postingDict, output_path + "\\posting")

    indexer.lda.initialModel(output_path)
    return indexer.lda


# def load_index(output_path):
#     print('Load inverted index')
#     inverted_index = utils.load_obj(output_path + "\\inverted_idx")
#     return inverted_index


def search_and_rank_query(query, num_docs_to_retrieve, p, output_path, lda):
    searcher = Searcher(p, output_path, lda)
    relevant_docs = searcher.relevant_docs_from_posting(query)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, num_docs_to_retrieve)


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve=2000):
    # with open(queries + '\\a.txt', 'r') as reader:
    #     print(reader.read())

    lda = run_engine(corpus_path, output_path, stemming)
    print("start query")
    # inverted_index = load_index(output_path)
    # lda = 5

    pa = Parse(stemming)
    if isinstance(queries, list):
        j = 1
        for query in queries:
            i = 0
            tweetid_rank = []
            print("the results for query: " + str(query) + ". are:")
            for tweetId in search_and_rank_query(query, num_docs_to_retrieve, pa, output_path, lda):
                print(str(i) + '. tweet id: ' + str(tweetId[0]))
                tweetid_rank.append(tweetId)
                i += 1
            if j == 1:
                write_result_to_csv(output_path, tweetid_rank)
            else:
                add_result_to_csv(output_path, tweetid_rank)
            j += 1
    else:
        try:
            file = open(queries, encoding="utf8")
            j = 1
            for line in file:
                i = 1
                tweetid_rank = []
                if line == '\n' or line == '':
                    continue
                print(str(j) + ". the results for query: " + str(line)[3:-2] + ". are:")
                for tweetId in search_and_rank_query(line[3:-2], num_docs_to_retrieve, pa, output_path, lda):
                    # print(str(i) + '. tweet id: ' + str(tweetId[0]))
                    tweetid_rank.append(tweetId)
                    i += 1
                if j == 1:
                    write_result_to_csv(output_path, tweetid_rank)
                else:
                    add_result_to_csv(output_path, tweetid_rank)
                j += 1
            file.close()
        except:
            print("not working")


def write_result_to_csv(output_path, tweetid_rand):
    with open(output_path + '\\results.csv', 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerow(tweetid_rand)


def add_result_to_csv(output_path, tweetid_rank):
    with open(output_path + '\\results.csv', 'a', newline='') as file:
        # file.writelines(tweetid_rank)
        wr = csv.writer(file)
        wr.writerow(tweetid_rank)
