import argparse
import metapy
import re


SENTENCE = re.compile(r"[^.!?]+")
WORD_REGEX = re.compile(r"[\w']+")



def pos_words_split():
    pos_words = open("positive-words.txt", 'r')

    pos_words_list = []
    for pos_line in pos_words:
        pos_word = pos_line.split("\n")
        pos_words_list.append(pos_word[0])

    return pos_words_list


def neg_words_split():
    neg_words = open("negative-words.txt", 'r')

    neg_words_list = []
    for neg_line in neg_words:
        neg_word = neg_line.split("\n")
        neg_words_list.append(neg_word[0])

    return neg_words_list

def read_article(article_filename):
    article = open(article_filename, 'r')
    article_str = article.read()
    return article_str

def write_to_file(text, file):
    if file == "summarizer":
        file_out = open("article_summary.txt", 'w')
    elif file == "tweets":
        file_out = open("relevant_tweets.txt", 'w')
    file_out.write(text)


'''
    Output:
        returns a dictionary of words as keys and the word count as value
'''
def extract_tokens(doc):

    tok = metapy.analyzers.ICUTokenizer()

    # lowercase all words so comparison is easier
    tok = metapy.analyzers.LowercaseFilter(tok)

    # stemming the words so similar words will be counted as one
    tok = metapy.analyzers.Porter2Filter(tok)

    # emoving stopwords so only words that enhance the meaning of the sentence remain
    tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)

    # counting occurrences of individual words
    ana = metapy.analyzers.NGramWordAnalyzer(1, tok)
    word_count = ana.analyze(doc)
    keys = word_count.keys()

    # making sure the keys returned by NGramWordAnalyzer are actually words
    for key in keys:
        word = WORD_REGEX.findall(key)
        if len(word) == 0 or key == "</s>" or key == "<s>" or key == "</p>" or key == "<p>":
            word_count[key] = 0

    return word_count


'''
    Input:
        Uses dictionary of word:word_count to score sentences in the article

    Output:
        String format of the article summary

    - Sentence scoring is done by accumulating the count of words present in the sentence
    - Threshold for sentence to be included in the summary is determined by if the sentence
        has a higher score than the average score of all the sentences in the document

'''
def sentence_summarizer(doc, trigrams):
    sentences = SENTENCE.findall(doc.content())

    # scoring sentences
    dict_sentence = {}
    for sentence in sentences:
        for word in trigrams:
            if word in sentence.lower():
                if sentence in dict_sentence:
                    dict_sentence[sentence] += trigrams[word]
                else:
                    dict_sentence[sentence] = trigrams[word]

    # calculating the average score of the sentences
    tot = 0
    for sent in dict_sentence:
        tot += dict_sentence[sent]

    avg_score = tot/len(dict_sentence)


    # filtering out sentences that have smaller score
    summarizer = "ARTICLE SUMMARIZED: \n"
    for sent in dict_sentence:
        if dict_sentence[sent] >= avg_score:
            summarizer += "     - " + sent + "\n"

    return summarizer


'''
    Input:
        takes both tokens generated from tweet and article
    Output:
        returns if the tweet is relevant by getting top 3 word counts from article
        and checks if any of the words associated with those counts are present in the tweets
'''
def filter_tweets(token_tw, token_art):
    token_art = sorted(token_art.items(), key=lambda x: x[1], reverse=True)

    top_words = []
    new_score = -1
    count = 0
    for word in token_art:
        if new_score != word[1]:
            count += 1
        if count > 1:
            break
        top_words.append(word[0])

    for word in top_words:
        if word in token_tw:
            return True

    return False


'''
    Checks if any words in the tweet are present in the positive word list -
    if so, increment the positive count
'''
def pos_score_tweet(tweet):
    word_list = WORD_REGEX.findall(tweet)
    pos_score = 0
    for word in word_list:
        if word in pos_words_split():
            pos_score += 1

    return pos_score


'''
    Checks if any words in the tweet are present in the negative word list -
    if so, decrement the negative count
'''
def neg_score_tweet(tweet):
    word_list = WORD_REGEX.findall(tweet)
    neg_score = 0
    for word in word_list:
        if word in neg_words_split():
            neg_score -= 1

    return neg_score

'''
    Input:
        (tweet_text, tweet_date)
'''
def tweet_sent_analyze(tweet_data):
    neg_score = neg_score_tweet(tweet_data[0])
    pos_score = pos_score_tweet(tweet_data[0])

    tot = neg_score + pos_score
    return (tweet_data, tot)


'''
    compiles the relevant tweets which are determined by filter_tweets()
'''
def get_relevant_tweets(article_tokens):
    relevant_tweets = []
    twitter_data = open("twitter_sample.tsv", 'r')
    for line in twitter_data:
        tweet = line.split("\t")[2]
        date = line.split("\t")[0]
        date = date.split(" ")[0]
        doc = metapy.index.Document()
        doc.content(tweet)
        tokens_intweet = extract_tokens(doc)

        if filter_tweets(tokens_intweet, article_tokens):
            relevant_tweets.append((tweet, date))

    return relevant_tweets


'''
    Input:
        array of relevant tweets to compile scores
    Output:
        string format of tweets ordered by the day the tweet was made
'''
def get_scored_tweets(relevant_tweets):
    tweet_scores = []
    for tweet_data in relevant_tweets:
        tweet_scores.append(tweet_sent_analyze(tweet_data))

    sorted_tweets = sorted(tweet_scores, key=lambda x: x[0][1], reverse=False)
    output_str = "RELEVANT TWEETS: \n"
    for tweet in sorted_tweets:
        output_str += str(tweet[1]) + "\t" + "[" + str(tweet[0][1]) + "] " + tweet[0][0] + "\n"

    return output_str


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('article', help='File to load news article from')
    args = parser.parse_args()

    content = read_article(args.article)

    doc = metapy.index.Document()
    doc.content(content)

    article_tokens = extract_tokens(doc)

    summary_str = sentence_summarizer(doc, article_tokens)
    write_to_file(summary_str, "summarizer")

    relevant_tweets = get_relevant_tweets(article_tokens)

    sorted_scored_tweets = get_scored_tweets(relevant_tweets)
    write_to_file(sorted_scored_tweets, "tweets")


