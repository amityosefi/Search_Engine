import traceback

import pandas as pd
from functools import reduce

df = pd.read_csv('208472001.csv')

# df = pd.DataFrame(
#     {'query': [1, 1, 2, 2, 3], 'Tweet_id': [12345, 12346, 12347, 12348, 12349],
#      'label': [1, 0, 1, 1, 0]})


test_number = 0
results = []


def precision(df, single=False, query_number=None):
    """
        This function will calculate the precision of a given query or of the entire DataFrame
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param single: Boolean: True/False that tell if the function will run on a single query or the entire df
        :param query_number: Integer/None that tell on what query_number to evaluate precision or None for the entire DataFrame
        :return: Double - The precision
    """
    df = df.values
    if single:
        number_of_relevant_documents_retrieved = 0
        total_number_of_documents_retrieved = 0
        for tweet in df:
            x = tweet[0]
            y = tweet[1]
            z = tweet[2]
            if tweet[0] == query_number:
                if tweet[2] == 1:
                    number_of_relevant_documents_retrieved += 1
                total_number_of_documents_retrieved += 1
        if total_number_of_documents_retrieved == 0:
            result = 0
        else:
            result = float(number_of_relevant_documents_retrieved / total_number_of_documents_retrieved)
    else:
        results_per_query = {}  # key = query_num , value = [number_of_relevant_documents_retrieved, total_number_of_documents_retrieved]
        for tweet in df:
            if tweet[2] == 1:
                if tweet[0] in results_per_query:
                    results_per_query[tweet[0]][0] += 1
                    results_per_query[tweet[0]][1] += 1
                else:
                    results_per_query[tweet[0]] = [1, 1]
            else:
                if tweet[0] in results_per_query:
                    results_per_query[tweet[0]][1] += 1
                else:
                    results_per_query[tweet[0]] = [0, 1]
        sum_of_precisions_per_query = 0
        for query in results_per_query.values():
            sum_of_precisions_per_query += query[0] / query[1]
        result = float(sum_of_precisions_per_query / len(results_per_query))

    return result


# recall(df, {1:2}, True) == 0.5
# recall(df, {1:2, 2:3, 3:1}, False) == 0.388
def recall(df, num_of_relevant):
    """
    This function will calculate the recall of a specific query or of the entire DataFrame
    :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
    :param num_of_relevant: Dictionary: number of relevant tweets for each query number. keys are the query number and values are the number of relevant.
    :return: Double - The recall
    """
    df = df.values
    num_of_found_relevant = 0
    temp_relevant_dict = {}
    if len(num_of_relevant) == 0:
        return None

    if len(num_of_relevant) == 1:
        query_lst = list(num_of_relevant.keys())
        specific_query = query_lst[0]
        for tweet in df:
            if tweet[0] == specific_query:
                if tweet[2] == 1:
                    num_of_found_relevant += 1
        if num_of_relevant[specific_query] == 0:
            result = None
        else:
            result = num_of_found_relevant / num_of_relevant[specific_query]
    else:
        for tweet in df:
            if tweet[0] in num_of_relevant:
                if tweet[0] not in temp_relevant_dict:
                    temp_relevant_dict[tweet[0]] = 0
                if tweet[2] == 1:
                    temp_relevant_dict[tweet[0]] += 1

        number_of_relavant = 0
        sum_recall = 0
        for tweet in temp_relevant_dict:
            if num_of_relevant[tweet] == 0:
                continue

            number_of_relavant += 1
            specific_recall = temp_relevant_dict[tweet] / num_of_relevant[tweet]
            sum_recall += specific_recall

        result = sum_recall / number_of_relavant

    return result


# precision_at_n(df, 1, 2) == 0.5
# precision_at_n(df, 3, 1) == 0
def precision_at_n(df, query_number=1, n=5):
    """
        This function will calculate the precision of the first n files in a given query.
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param query_number: Integer that tell on what query_number to evaluate precision
        :param n: Total document to splice from the df
        :return: Double: The precision of those n documents
    """
    if n == 0:
        return 0
    df = df.values
    number_of_relevant_documents_retrieved = 0
    counter_until_n = 0
    for tweet in df:
        if tweet[0] == query_number:
            counter_until_n += 1
            if tweet[2] == 1 and counter_until_n <= n:
                number_of_relevant_documents_retrieved += 1
    if counter_until_n < n and counter_until_n != 0:
        result = float(number_of_relevant_documents_retrieved / counter_until_n)
    else:
        result = float(number_of_relevant_documents_retrieved / n)
    return result


# map(df) == 2/3
def map(df):
    """
        This function will calculate the mean precision of all the df.
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :return: Double: the average precision of the df
    """
    df_map = df.values
    query_precision = {}
    num_tweets_of_query_dict_counter = {}  # key = query_num , value = counter

    for tweet in df_map:
        if tweet[2] == 0:
            if tweet[0] not in query_precision:
                query_precision[tweet[0]] = 0
                num_tweets_of_query_dict_counter[tweet[0]] = 1
        elif tweet[0] not in query_precision:
            num_tweets_of_query_dict_counter[tweet[0]] = 1
            query_precision[tweet[0]] = 1
        else:
            num_tweets_of_query_dict_counter[tweet[0]] += 1
            query_precision[tweet[0]] += precision_at_n(df, tweet[0],
                                                              num_tweets_of_query_dict_counter[tweet[0]])

    AvgPresicion = {}
    for query in num_tweets_of_query_dict_counter:
        x = query
        AvgPresicion[query] = float(query_precision[query] / num_tweets_of_query_dict_counter[query])

    map_result = 0
    for res in AvgPresicion.values():
        map_result += res

    if len(AvgPresicion) == 0:
        return 0
    else:
        result = float(map_result / len(AvgPresicion))
        return result



def test_value(func, expected, variables):
    """
        This function is used to test your code. Do Not change it!!
        :param func: Function: The function to test
        :param expected: Float: The expected value from the function
        :param variables: List: a list of variables for the function
    """
    global test_number, results
    test_number += 1
    result = func(*variables)
    try:
        result = float(f'{result:.3f}')
        if abs(result - float(f'{expected:.3f}')) <= 0.01:
            results.extend([f'Test: {test_number} passed'])
        else:
            results.extend([f'Test: {test_number} Failed running: {func.__name__}'
                            f' expected: {expected} but got {result}'])
    except ValueError as ve:
        results.extend([f'Test: {test_number} Failed running: {func.__name__}'
                        f' value return is not a number'])
    except:
        d = traceback.format_exc().splitlines()
        results.extend([f'Test: {test_number} Failed running: {func.__name__} with the following error: {" ".join(d)}'])


# test_value(precision, 0.5, [df, True, 1])
# test_value(precision, 0.5, [df, False, None])
# test_value(recall, 0.5, [df, {1: 2}])
# test_value(recall, 0.388, [df, {1: 2, 2: 3, 3: 1}])
# test_value(precision_at_n, 0.5, [df, 1, 2])
# test_value(precision_at_n, 0, [df, 3, 1])
# test_value(map, 2 / 3, [df])

#
# # Amit's tests on 311277438.csv
#
# # precision
# test_value(precision, 3 / 8, [df, True, 1])
# test_value(precision, 7 / 8, [df, True, 2])
# test_value(precision, 1, [df, True, 3])
# test_value(precision, 0, [df, True, 88])
# test_value(precision, 0.659375, [df, False, None])
#
# # recall
# test_value(recall, 3 / 20, [df, {1: 20}])
# test_value(recall, 3 / 5, [df, {1: 5}])
# test_value(recall, 0, [df, {100: 5}])
# # test_value(recall, None, [df, {1: 0}])
# test_value(recall, (3 / 20 + 7 / 8 + 8 / 10) / 3, [df, {1: 20, 2: 8, 3: 10}])
# test_value(recall, (6 / 17 + 0.5 + 2 / 9) / 3, [df, {27: 17, 30: 8, 39: 9}])
# test_value(recall, (6 / 17 + 2 / 9) / 2, [df, {27: 17, 30: 0, 39: 9}])
#
#
# # precision_at_n
# test_value(precision_at_n, 3 / 8, [df, 1, 8])
# test_value(precision_at_n, 3 / 8, [df, 1, 20])
# test_value(precision_at_n, 2 / 3, [df, 1, 3])
# test_value(precision_at_n, 4 / 7, [df, 5, 7])
# test_value(precision_at_n, 0, [df, 7, 1])
# test_value(precision_at_n, 1, [df, 8, 1])
# test_value(precision_at_n, 0, [df, 88, 1])



# Shahar's tests on 208472001.csv
#
# precision
test_value(precision, 6 / 8, [df, True, 1])
test_value(precision, 5 / 8, [df, True, 2])
test_value(precision, 6 / 8, [df, True, 3])
test_value(precision, 0, [df, True, 88])
test_value(precision, 0.60625, [df, False, None])

# recall
test_value(recall, 6 / 20, [df, {1: 20}])
test_value(recall, 6 / 8, [df, {1: 8}])
test_value(recall, 0, [df, {100: 5}])
# test_value(recall, None, [df, {1: 8, 30: 0}])


# precision_at_n
test_value(precision_at_n, 6 / 8, [df, 1, 8])
test_value(precision_at_n, 6 / 8, [df, 1, 20])
test_value(precision_at_n, 2 / 3, [df, 1, 3])
test_value(precision_at_n, 0, [df, 88, 1])
#
for res in results:
    print(res)

