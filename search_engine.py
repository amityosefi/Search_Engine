import csv
import time

from LDAModel import LDA
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from smart_open import open
from searcher import Searcher

def run_engine(corpus_path, output_path, stemming=False):
    """

    :param corpus_path: path for parquet files
    :param output_path: path to write pickle files
    :param stemming: boolean to use stemming or not
    :return:
    """
    start = time.time()

    ConfigClass(corpus_path, output_path, stemming)
    r = ReadFile(corpus_path)
    p = Parse(stemming)
    indexer = Indexer(output_path)

    if corpus_path.endswith('parquet'):
        documents_list = r.read_file(corpus_path)
        parseAndIndexDocuments(documents_list, p, indexer)
    else:
        documents_list = r.read_dir()

        while documents_list:
            parseAndIndexDocuments(documents_list, p, indexer)
            documents_list = r.read_dir()
    # Iterate over every document in the file
    # documents_list = documents_list[:500]


    documents_list.clear()

    print("start merge files")
    s = time.time()
    indexer.merge_posting_files()
    e = time.time() - s
    print("merge time: " + str(e) + " secs.")
    lda = LDA(output_path)
    lda.build_ldaModel()

    x = str(indexer.count)
    en = time.time()-start
    print("the time takes the hole reader parser and indexer after merge files "
          "and building the model for " + x + " documents are: " + str(en) + " sec")


def parseAndIndexDocuments(documents_list, p, indexer):
    for idx, document in enumerate(documents_list):

        # parse the document
        parsed_document = p.parse_doc(document)
        # parsed_document = p.parse_doc(documents_list[32841])

        # index the document data
        indexer.add_new_doc(parsed_document)


def search_and_rank_query(query, num_docs_to_retrieve, searcher):

    relevant_docs, query_tokens = searcher.relevant_docs_from_posting(query)
    ranked_relevant_docs = searcher.ranker.rank_relevant_doc(relevant_docs, query_tokens)
    most_relevent_docs = searcher.ranker.retrieve_top_k(ranked_relevant_docs, num_docs_to_retrieve)
    return most_relevent_docs


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve=2000):

    run_engine(corpus_path, output_path, stemming)
    print("start query")
    # lda = 5

    pa = Parse(stemming)
    searcher = Searcher(pa, output_path)
    searcher.ranker.load_docs_and_terms()

    if isinstance(queries, list):
        j = 1
        for query in queries:
            i = 0
            tweetid_rank = []
            print("the results for query: " + str(query) + ". are:")
            for tweetId in search_and_rank_query(query, num_docs_to_retrieve, searcher):
                print(str(i) + '. tweet id: ' + str(tweetId))
                tweetid_rank.append(tweetId)
                i += 1
            if j == 1:
                write_result_to_csv(output_path, tweetid_rank)
            else:
                add_result_to_csv(output_path, tweetid_rank)
            j += 1
    else:
    # try:
        file = open(queries, encoding="utf8")
        j = 1
        for line in file:
            i = 1
            tweetid_rank = []
            if line == '\n' or line == '':
                continue
            line = str(line[3:-2])
            print(str(j) + ". the results for query: " + line + ". are:")
            for tweetId in search_and_rank_query(line, num_docs_to_retrieve, searcher):
                # print(str(i) + '. tweet id: ' + str(tweetId[0]))
                tweetid_rank.append(tweetId)
                i += 1
            if j == 1:
                write_result_to_csv(output_path, tweetid_rank)
            else:
                add_result_to_csv(output_path, tweetid_rank)
            j += 1
        file.close()
    # except:
    #     print("not working")


def write_result_to_csv(output_path, tweetid_rand):
    with open(output_path + '\\results.csv', 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerow(tweetid_rand)


def add_result_to_csv(output_path, tweetid_rank):
    with open(output_path + '\\results.csv', 'a', newline='') as file:
        wr = csv.writer(file)
        wr.writerow(tweetid_rank)
