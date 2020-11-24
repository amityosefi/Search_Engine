from nltk.corpus import stopwords
from document import Document
from nltk.stem import LancasterStemmer
import re


class Parse:
    corpus_dict = {}

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.stop_words.extend(["RT", "rt", "rT", "Rt"])
        ##self.lancaster =LancasterStemmer()

    def parse_sentence(self, text):

        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        text_splitted= text.split()
        #stop_words = stopwords.words('english')
        ##lancaster = LancasterStemmer()
        i = 0
        while i < len(text_splitted):
            try:
                word = text_splitted[i].strip('[').strip(']').strip('(').strip(')').strip('{').strip('}')
                word = re.sub('[^A-z%_@#.,!?$/0-9]', '', word)
                if word[len(word) - 1] == '%':
                    word = word[:len(word)-1]
                    if word.isdigit() or re.search(r'^-?[0-9]+\.[0-9]+$', word) or re.search(r'^-?[0-9]+\/[0-9]+$', word):
                        number = self.parse_numbers(word)
                        percent_number = str(number) + '%'
                        self.text_tokens.append(percent_number)
                        i += 1
                        continue
                    elif word == '%':
                            self.text_tokens.append('1%')
                    else:
                        word = re.sub('[^A-z.0-9]', '', word)
                        if word != '':
                            self.text_tokens.append(word)
                    i += 1
                    continue
                elif word.isdigit() or re.search(r'^-?[0-9]+\.[0-9]+$', word) or re.search(r'^-?[0-9]+\/[0-9]+$', word):
                    if i < len(text_splitted) - 1:
                        next_word = re.sub('[^A-z%_@#.,!?$/0-9]', '', text_splitted[i + 1])
                        number = self.parse_numbers(word, next_word)
                        if number.endswith('K') or number.endswith('B') or number.endswith('M'):
                            i += 1
                        elif (next_word == 'percent') or (next_word == 'percentage'):
                            number = str(word) + '%'
                            i += 1
                        self.text_tokens.append(number)
                        i += 1
                    else:
                        number = self.parse_numbers(word)
                        self.text_tokens.append(number)
                        i += 1
                    continue
            except:
                ## token is not a number
                word = re.sub('[^A-z%_@#.,!?$/0-9]', '', text_splitted[i])

            if word.startswith('https'):
                i += 1
                continue

            word = re.sub(r'([?!/,.]+)',r',',word)
            words = word.split(',')
            for word in words:
                if (len(word) > 0) and (word.isspace() == False) and word.lower() not in self.stop_words:
                    if (word[0] == '#'):
                        word = word[1:]
                        hashtags = word.split('#')
                        for h in hashtags:
                            h = re.sub('[^A-z_0-9]', '', h)
                            if h != '':
                                self.parse_hashtags(h)
                    elif word[0] == '@':
                        word = word[1:]
                        tags = word.split('@')
                        for t in tags:
                           t = re.sub('[^A-z_0-9]', '', t)
                           if t != '':
                            self.parse_tags(t)
                    elif word[0] == '"' or word[0] == "'" or word[0] == '‘' or word[0] == '’':
                        iterations = self.parse_quote(word, i, text_splitted)
                        i += iterations
                        continue
                    else:
                        ##word = word.lower()
                        ##word = lancaster.stem(word)
                        word = re.sub('[^A-Za-z0-9]', '', word)
                        if word != '':
                            self.text_tokens.append(word)
            i += 1

        ##print(self.text_tokens)

    def parse_tags(self, word):
        word = re.sub('[^A-z$_0-9]', '', word)
        temp = re.sub('[^A-Za-z$0-9]', '', word)
        if temp != '':
            t_word = '@' + str(word)
            self.text_tokens.append(t_word)

    def parse_quote(self, word, i, text_splitted):

            start_iterations = i
            word = str(word)
            if word[len(word) - 1] == '"' or word[len(word) - 1] == "'" or word[len(word) - 1] == '‘' or word[len(word) - 1] == '’':
                self.text_tokens.append(word.upper().strip('"').strip('"').strip('‘'))
            else:
                quote = word
                while True:
                    if i < len(text_splitted) - 1:
                        next_word = re.sub('[^A-z%_@#.,!?$/0-9]', '', text_splitted[i + 1])
                        if len(next_word) == 0:
                            i += 1
                        elif (next_word[len(next_word) - 1] == "'") or (next_word[len(next_word) - 1] == '"') or (next_word[len(next_word)-1] == '‘') and (next_word[len(next_word)-1] == '’'):
                            quote += ' ' + next_word
                            self.text_tokens.append(quote.upper().strip('"').strip("'").strip('‘').strip('’'))
                            i += 1
                            break
                        else:
                            quote += ' ' + next_word
                            i += 1
                    elif i == (len(text_splitted) - 1):
                        self.text_tokens.append(quote.upper().strip('"').strip("'").strip('‘').strip('’'))
                        break

            return i - start_iterations + 1

    def parse_hashtags(self, element):

        element = element.replace(' ', '')
        expanded = " ".join([a for a in re.split('([A-Z][a-z]+)', element) if a])
        hashtag_tokens = expanded.split(' ')
        for w in hashtag_tokens:
            if w != '' and '_' not in w:
                self.text_tokens.append(w)
        word = re.sub('[^A-z$_0-9]', '', element)
        temp = re.sub('[^A-Za-z%$0-9]', '', word)
        if temp != '':
            self.text_tokens.append('#'+element)

    def parse_url(self, term_dict, url):
        stop_words = stopwords.words('english')
        name = ''
        for character in url:
            if character == ' ':
                break
            if ('a' <= character <= 'z') or ('A' <= character <= 'Z') or ('0' <= character <= '9') or (
                    character == '.'):
                name += character
            elif (len(name) > 1) or (
                    (len(name) == 1) and ('a' <= name <= 'z') or ('A' <= name <= 'Z') or ('0' <= name <= '9')):
                ##if name.isdigit():
                  ##  name = self.parse_numbers(name)
                if name.lower() not in stop_words:
                    if name not in term_dict.keys():
                        name = str(name).lower()
                        term_dict[name] = 1
                    else:
                        term_dict[name] += 1
                name = ''
        if (len(name) > 1) or (
                (len(name) == 1) and ('a' <= name <= 'z') or ('A' <= name <= 'Z') or ('0' <= name <= '9')):
            ##if name.isdigit():
              ##  name = self.parse_numbers(name)
            if name.lower() not in stop_words:
                if name not in term_dict.keys():
                    name = str(name).lower()
                    term_dict[name] = 1
                else:
                    term_dict[name] += 1

        return term_dict

    def parse_numbers(self, item, next_i=''):
        r = ['', 'K', 'M', 'B']

        if bool(re.search(r'^-?[0-9]+\.[0-9]+$', item)):
            return item
        elif bool(re.search(r'^-?[0-9]+\/[0-9]+$', next_i)) and float(item) <= 999:
            return item + ' ' + next_i
        elif bool(re.search(r'^-?[0-9]+\/[0-9]+$', item)):
            return item
        elif (next_i == "Thousand" or next_i == "thousand") and float(item) <= 9999:
            return item + "K"
        elif (next_i == "M" or next_i == "m" or next_i == "Million" or next_i == "million") and float(item) <= 9999:
            return item + "M"
        elif (next_i == "B" or next_i == "b" or next_i == "Billion" or next_i == "billion") and float(item) <= 9999:
            return item + "B"

        num = float(item)
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
            if magnitude >= 3:
                break
        return str("%.3f" % num).rstrip("0").rstrip(".") + '' + str(r[magnitude])


    def parse_doc(self, doc_as_list):
        """commi
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """

        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        term_dict = {}
        self.text_tokens = []
        ##print(full_text)
        self.parse_sentence(full_text)

        if (url is not None) and (url != '{}'):
            updated_dict = self.parse_url(term_dict, url)
            term_dict = updated_dict

        if (quote_text is not None) and (quote_text != '{}'):
            updated_dict = self.parse_url(term_dict, quote_text)
            term_dict = updated_dict

        str_retweet_url = str(retweet_url)
        url_retweet_url_index = str_retweet_url.find('https')
        if url_retweet_url_index != -1:
            url_retweet_url = str_retweet_url[url_retweet_url_index:]
            if (url_retweet_url is not None) and (url_retweet_url != '{}'):
                updated_dict = self.parse_url(term_dict, url_retweet_url)
                term_dict = updated_dict

        doc_length = len(self.text_tokens)  # after text operations.4

        for term in self.text_tokens:
            if term not in term_dict.keys():
                term = str(term).lower()
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        # Parse.corpus_dict.update(term_dict)
        #print(term_dict)

        max_tf = 0
        # Parse.corpus_dict.update(term_dict)
        for item in term_dict.values():
            if max_tf < item:
                max_tf = item

        # print(full_text)
        # print(self.text_tokens)
        # print(term_dict)
        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length, max_tf, len(term_dict))

        return document