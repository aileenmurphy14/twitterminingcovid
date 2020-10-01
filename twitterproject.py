import sys,tweepy,csv,re
from textblob import TextBlob
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import pandas as pd 
from nltk.corpus import stopwords
sw = stopwords.words("english")
newStopWords = ['new', 'will', 'one', 'now', 'says', 'many', 'dont', 're', 'th', 'go', 'time', 'via', 'thats', 'im', 'like', 'could', 'back', 'coronavirus']
sw.extend(newStopWords)

class SentimentAnalysis:

    def __init__(self):
        self.tweets = []
        self.tweetText = []

    def getTweets(self):

        searchTerm = "coronavirus"      #term used to search through tweets
        NoOfTerms = 10000           #number of tweets to search for

        polarity = 0
        positive = 0
        wpositive = 0
        spositive = 0
        negative = 0
        wnegative = 0
        snegative = 0
        neutral = 0

        consumer_key = ""
        consumer_secret = ""
        access_token = ""
        access_token_secret = ""

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        api = tweepy.API(auth)

        #gets 10,000 tweets about coronavirus since 4/24/20. Filters out retweets. 
        self.tweets = tweepy.Cursor(api.search, q='coronavirus -filter:retweets', count = 100, lang="en", since="2020-04-24", include_rts = False).items(NoOfTerms)

        csvFile = open('tweets.txt', 'a')   #to put tweets
        csvWriter = csv.writer(csvFile) 
        csvFile2 = open('locations.txt', 'a')   #to put locations
        csvWriter2 = csv.writer(csvFile2)
        states = ['alabama','al','alaska','ak','arizona','az','arkansas','ar','california','ca','colorado','co','connecticut','ct','delaware','de','district of columbia','dc','florida','fl',\
            'georgia','ga','hawaii','hi','idaho','id','illinois','il','indiana','in','iowa','ia','kansas','ks','kentucky','ky','louisiana','la','maine','me','maryland','md','massachusetts','ma',\
            'michigan','mi','minnesota','mn','mississippi','ms','missouri','mo','montana','mt','nebraska','ne','nevada','nv','new hampshire','nh','new jersey','nj','new mexico','nm','new york','ny',\
            'north carolina','nc','north dakota','nd','ohio','oh','oklahoma','ok','oregon','or','pennsylvania','pa','rhode island','ri','south carolina','sc','south dakota','sd','tennessee','tn',\
            'texas','tx','utah','ut','vermont', 'vt','virginia','va','washington','wa','west virginia', 'wv','wisconsin', 'wi','wyoming','wy']
        # iterating through tweets fetched for location
        for tweet in self.tweets:
            if(tweet.user.location is not None):
                loc = tweet.user.location.lower()
                loc = re.sub('[^A-Za-z0-9 ]+', '', loc)  # remove punctuation except spaces
                loc = loc.split()
                for i in loc:
                    if i in states:
                        c = states.index(i)
                        if len(i) ==2:
                            csvWriter2.writerow([i])
                        elif i == 'nyc':
                            csvWriter2.writerow(['ny'])
                        else:
                            csvWriter2.writerow([states[c+1]])
                    
            #Append to temp so that we can store in csv later. I use encode UTF-8
            self.tweetText.append(self.cleanTweet(tweet.text))
            analysis = TextBlob(tweet.text)
            polarity += analysis.sentiment.polarity  # adding up polarities to find the average later

            if (analysis.sentiment.polarity == 0):  # adding reaction of how people are reacting to find average later
                neutral += 1
            elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
                wpositive += 1
            elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
                positive += 1
            elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
                spositive += 1
            elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
                wnegative += 1
            elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
                negative += 1
            elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
                snegative += 1


        # Write to csv and close csv file

        csvWriter.writerow(self.tweetText)
        csvFile.close()
        csvFile2.close()
        # finding average of how people are reacting
        positive = self.percentage(positive, NoOfTerms)
        wpositive = self.percentage(wpositive, NoOfTerms)
        spositive = self.percentage(spositive, NoOfTerms)
        negative = self.percentage(negative, NoOfTerms)
        wnegative = self.percentage(wnegative, NoOfTerms)
        snegative = self.percentage(snegative, NoOfTerms)
        neutral = self.percentage(neutral, NoOfTerms)

        # finding average reaction
        polarity = polarity / NoOfTerms

        # printing out data
        print("How people are reacting about coronavirus by analyzing ", NoOfTerms , " tweets.")
        print()
        print("Popular Tweets are: ")

        if (polarity == 0):
            print("Neutral")
        elif (polarity > 0 and polarity <= 0.3):
            print("Weakly Positive")
        elif (polarity > 0.3 and polarity <= 0.6):
            print("Positive")
        elif (polarity > 0.6 and polarity <= 1):
            print("Strongly Positive")
        elif (polarity > -0.3 and polarity <= 0):
            print("Weakly Negative")
        elif (polarity > -0.6 and polarity <= -0.3):
            print("Negative")
        elif (polarity > -1 and polarity <= -0.6):
            print("Strongly Negative")

        print()
        print("Detailed Report: ")
        print(str(positive) + "% people thought it was positive")
        print(str(wpositive) + "% people thought it was weakly positive")
        print(str(spositive) + "% people thought it was strongly positive")
        print(str(negative) + "% people thought it was negative")
        print(str(wnegative) + "% people thought it was weakly negative")
        print(str(snegative) + "% people thought it was strongly negative")
        print(str(neutral) + "% people thought it was neutral")

        self.plotPieChart(positive, wpositive, spositive, negative, wnegative, snegative, neutral, searchTerm, NoOfTerms)


    def cleanTweet(self, t):
        t = t.lower();
        t = re.sub(r'http\S+', ' ', t)  # remove url's
        t = re.sub("[^\x00-\x7F]+", ' ', t)  # replace consecutive non-ASCII values
        t = re.sub('[^A-Za-z0-9 ]+', '', t)  # remove punctuation except spaces
        return t

    # function to calculate percentage
    def percentage(self, part, whole):
        temp = 100 * float(part) / float(whole)
        return format(temp, '.2f')

    def plotPieChart(self, positive, wpositive, spositive, negative, wnegative, snegative, neutral, searchTerm, noOfSearchTerms):
        labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]','Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]',
                  'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]', 'Strongly Negative [' + str(snegative) + '%]']
        sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
        colors = ['yellowgreen','lightgreen','darkgreen', 'gold', 'red','lightsalmon','darkred']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.title('How people are reacting on ' + searchTerm + ' by analyzing ' + str(noOfSearchTerms) + ' Tweets.')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

#gets number of each state tweeted from
def getFreqStates():
    states = []
    with open("locations.txt") as r:
        lines = [line.rstrip() for line in r]
    for i in lines:
        states.append(i)
    states = sorted(states)
    wordsToCount =(word for word in states)
    c = Counter(wordsToCount)
    plt.bar(c.keys(), c.values())
    plt.xticks(rotation=90)
    plt.show()

#gets 25 most common words in each tweet besides stopwords
def getFreqWords():
    c = Counter()
    with open('tweets.txt') as r:
        for line in r:
            spl = line.split(',')
            for s in spl:
                spl1 = s.split()
                c.update(w for w in spl1 if w not in sw and len(w) > 1 and w.isalpha())
    most_common = c.most_common(25)
    #print(most_common)
    fig = plt.figure(dpi = 80)
    ax = fig.add_subplot(1,1,1)
    table_data = most_common
    table = ax.table(cellText = table_data, loc = 'center')
    table.set_fontsize(10)
    ax.axis('off')
    plt.show()

#creates wordcloud of common words and phrases in tweets collected
def getWordcloud():
    tweetFile = open("tweets.txt").read()
    wordcloud = WordCloud(stopwords = sw, background_color = 'white', width = 1400, height = 1400).generate(tweetFile)
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()

if __name__== "__main__":
    sa = SentimentAnalysis()
    sa.getTweets()
    getFreqStates()
    getFreqWords()
    getWordcloud()
    

#SOURCES:
#https://stackoverflow.com/questions/42418085/python-wordcloud-from-a-txt-file
#https://chadrick-kwag.net/matplotlib-table-example/
#https://stackoverflow.com/questions/3594514/how-to-find-most-common-elements-of-a-list/44481414
# https://www.toptal.com/python/twitter-data-mining-using-python
# https://developer.twitter.com/en/docs/tutorials/filtering-tweets-by-location
#https://www.youtube.com/watch?v=eFdPGpny_hY
#https://github.com/the-javapocalypse/Twitter-Sentiment-Analysis/blob/master/main.py
