# Search_Engine
A search engine project base on corpus of 10 million twitts.

Each twitt, started with parser (tokenized) which remove all stopwords and irrelevant words and signs.

After the parser, the twitt go to indexer which save for each term in the twiit the twiitID.

After all the twiitts were indexed, we start using LDA model to which separates all the twitts to topics.

While there is a query, the searcher check on the LDA model which topic is more relevant and send all the twitts that are connected to the same topic.

Meanwhile the searcher sends the ranker each twitt and by cossime gets a rank.

First 100 twitts with the best score are save in a csv file.

#technology

* Based on python 3.7
* Needs to install all packages in requirements.txt file
