# Article Sentiment Analyzer

The program's goal is to read in a user inputted article and create a summary. Along with summary, it analyzes a set of tweets to find tweets that are relevant to the article and then create a timeline of changing sentiments related to the topic of the article.

## Getting Started

### Prerequisites

We use the MeTA toolkit in this project for text analysis
```
# Ensure your pip is up to date
pip install --upgrade pip

# install metapy
pip install metapy pytoml
```

## Running the Project

```
# to run the program
# the argument into the function must be a file with the text of the article - testcase has already been provided
# the twitter dataset provided is just a sample of small selection of tweets from June, 2009
python3 sum_creator.py test_article.txt
```

### Output

Two files will be create, article_summary.txt and relevant_tweets.txt. article_summary.txt will contain a summary of the article in bullet points and the relevant_tweets.txt will contain the list of relevant tweets in the format [sentiment score, date of tweet creation, tweet text].

### Test

Run with given test_article.txt file containing an article about the launch of the Iphone 3G. The relevant_tweets.txt will have 3 tweets about the iphone 3G launch and their sentiments and the article_summary.txt will contain a summary.
```
python3 sum_creator.py test_article.txt
```
## Implementation

### Summarizer
- We created a dictionary of words and their corresponding counts using stemming, removing stop-words and NGramWordAnalyzer
- Using this dictionary we scored each sentence by adding the word counts for each word that was present in the sentence
- We determined which sentences would be displayed in the summary by finding the average score for a sentence in the document and only using the sentences that had a higher score than the average

### Finding Relevant Tweets
- We determined if a tweet was relevant if it had the any of the words the were also in the top 3 highest counts from the word dictionary generated from the article. We only looked from at least one match because tweets very short so couldn't make the restrictions too tight in fear of loosing relevant tweets

### Sentiment Analysis on Tweets
- Using a compiled list of positive and negative words, we created a score for the tweet by checking if the words in the tweet were on either of the lists and subtracting or adding to the score. We weighted each of the sentiment words equally and did not normalize the weight based on length of tweet

## Authors

* **Renuka Nannapaneni** - created the summarizer for the article
* **Yashna Kumar** - create the sentiment and relevance analysis for the tweets


## License

This project is licensed under the  University of Illinois/NCSA Open Source License - see the [LICENSE.md](LICENSE.md) file for details

