from nltk.corpus import stopwords
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.text_tokens = []

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """

        text = str(text)
        text_splitted= text.split()

        for i in text_splitted:
                word = self.parse_delimiters(i.strip("'").strip('"'))
                if word not in self.stop_words:
                    if (len(word) > 0):
                        if (word[0] == '#'):
                            self.parse_hashtags(word[1:])
                           ## if word[1:].lower() not in self.text_tokens:
                             ##   self.text_tokens.append(word[1:].lower().replace('_', ''))
                            if word == word.upper():
                                self.text_tokens.append(word.replace('_', ''))
                            else:
                                self.text_tokens.append(word.lower().replace('_', ''))
                        elif (word == 'percent') or (word == 'percentage'):
                            self.parse_percent(word)
                        else:
                            word = word.lower()
                            self.text_tokens.append(word)

        print(self.text_tokens)
        ##text_tokenized = [w.lower() for w in text_tokens if w not in self.stop_words]

    def parse_delimiters(self, element):
        delimiters = ['!', '?', ':', '$', '^', '&', '*', '(', ')', '.', ',' '[', ']', '{', '}', ';', '+', '=']
        element = str(element)
        word = ''
        for char in element:
            if char not in delimiters:
                word += char

        return word.replace('-', ' ')

    def parse_hashtags(self, element):

        if element == element.upper():
            self.text_tokens.append(element.replace('_', ''))
        elif element != element.lower(): 
            name = ''
            for c in element:
                if c.isupper():
                    if name != '':
                        name = name.lower()
                        self.text_tokens.append(name)
                        name = ''
                    name += c
                elif c.islower():
                    name += c
                elif c == '_':
                    name = name.lower()
                    self.text_tokens.append(name)
                    name = ''
                elif '0' <= c <= '9':
                    name += c
            if name != '':
                if name.isnumeric():
                    old_name = self.text_tokens[len(self.text_tokens)-1]
                    new_name = str(old_name + name)
                    self.text_tokens.remove(old_name)
                    self.text_tokens.append(new_name.lower().replace('_', ''))
                else:
                    name = name.lower().replace('_', '')
                    self.text_tokens.append(name)

    def parse_percent(self, element):

        element = self.text_tokens[len(self.text_tokens)-1] + '%'
        self.text_tokens[len(self.text_tokens)-1] = element
       ## self.text_tokens[index - 1: index + 1] = [reduce(lambda i, j: i + j, self.text_tokens[index - 1: index + 1])]

    def parse_url(self, term_dict, url):
        name = ''
        for character in url:
            if ('a' <= character <= 'z') or ('A' <= character <= 'Z') or ('0' <= character <= '9') or (
                    character == '.'):
                name += character
            elif (len(name) > 1) or (
                    (len(name) == 1) and ('a' <= name <= 'z') or ('A' <= name <= 'Z') or ('0' <= name <= '9')):
                if name not in term_dict.keys():
                    term_dict[name] = 1
                else:
                    term_dict[name] += 1
                name = ''
        if (len(name) > 1) or (
                (len(name) == 1) and ('a' <= name <= 'z') or ('A' <= name <= 'Z') or ('0' <= name <= '9')):
            if name not in term_dict.keys():
                term_dict[name] = 1
            else:
                term_dict[name] += 1

        return term_dict

    def parse_doc(self, doc_as_list):
        """
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
                updated_dict = self.parse_url(term_dict, retweet_url)
                term_dict = updated_dict

        doc_length = len(self.text_tokens)  # after text operations.

        for term in self.text_tokens:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document
