import csv
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

    ConfigClass(corpus_path, output_path, stemming)
    r = ReadFile(corpus_path)
    p = Parse(stemming)
    indexer = Indexer(output_path, stemming)

    if corpus_path.endswith('parquet'):
        documents_list = r.read_file(corpus_path)
        parseAndIndexDocuments(documents_list, p, indexer)
    else:
        documents_list = r.read_dir()

        while documents_list:
            parseAndIndexDocuments(documents_list, p, indexer)
            documents_list = r.read_dir()

    documents_list.clear()
    indexer.merge_posting_files()

    lda = LDA(output_path, indexer.dictdoc, stemming)
    lda.build_ldaModel()


def parseAndIndexDocuments(documents_list, p, indexer):
    # documents_list = documents_list[:20000]
    for idx, document in enumerate(documents_list):
        # parse the document
        parsed_document = p.parse_doc(document)
        # parsed_document = p.parse_doc(documents_list[32841])

        # index the document data
        indexer.add_new_doc(parsed_document)


def search_and_rank_query(query, num_docs_to_retrieve, searcher):

    (relevant_docs, query_tokens, docslen) = searcher.relevant_docs_from_posting(query)
    ranked_relevant_docs = searcher.ranker.rank_relevant_doc(relevant_docs, query_tokens, docslen)
    most_relevent_docs = searcher.ranker.retrieve_top_k(ranked_relevant_docs, num_docs_to_retrieve)
    return most_relevent_docs


def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve=2000):

    if stemming:
        output_path = output_path + '\\WithStem'
    else:
        output_path = output_path + '\\WithoutStem'

    run_engine(corpus_path, output_path, stemming)

    pa = Parse(stemming)
    searcher = Searcher(pa, output_path, stemming)
    # searcher.ranker.load_docs_and_terms()
    write_result_to_csv()

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
            print(str(i) + '. Tweet id: {' + str(tweetId[0]) + '} Score: {' + str(tweetId[1]) + '}')
            tweetid_rank.append(tweetId)
            i += 1
        add_result_to_csv(j, tweetid_rank)
        j += 1
    file.close()


def write_result_to_csv():
    with open('results.csv', 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerow(['Query_num', 'Tweet_id', 'Rank'])


def add_result_to_csv(numquery, tweetid_rank):
    with open('results.csv', 'a', newline='') as file:
        wr = csv.writer(file)
        for item in tweetid_rank:
            x = [str(numquery)] + item
            wr.writerow(x)
