
# coding: utf-8

# Import the library

# In[2]:

import tweepy
from tweepy.streaming import StreamListener
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Authentication

# In[82]:

Consumer_Key    = 'jypioHVEm55HyWBOusZw1ICiM'
Consumer_Secret = 'vBjVAyJwQY1zKxCaTPYqqOgST7YLRhcTIvWcunTQFPUtCqTwYJ'
Access_Token    = '964193901115473920-mq6fZZJoVTo9VoytINW3GalpjgCmXvm'
Access_Token_Secret = 'G4T5I089sUvoMJ4OfQlkDxxsAdpn7Dv9ZRj074ITIH4fJ'
Owner_ID = 964193901115473920
auth = tweepy.OAuthHandler(Consumer_Key, Consumer_Secret)
auth.set_access_token(Access_Token, Access_Token_Secret)

api = tweepy.API(auth)


# Testing the water

# In[83]:


public_tweets = api.home_timeline()
for tweet in public_tweets:
    print (tweet.text)


# For example the following code returns to us an User model:

# In[84]:

user = api.get_user('Kyle_kc2980')
user


# Models contain the data and some helper methods which we can then use

# In[85]:

print (user.screen_name) 
print (user.followers_count) 
for friend in user.friends():
   print (friend.screen_name)


# In[44]:

public_tweets = api.user_timeline('realDonaldTrump')
for tweet in public_tweets:
    print (tweet.text)


# ### Rest API

# Searching for Tweets
# API.search(q[, lang][, locale][, rpp][, page][, since_id][, geocode][, show_user])
# 
#     Returns tweets that match a specified query.
#     Parameters: 
# 
#         q – the search query string
#         lang – Restricts tweets to the given language, given by an ISO 639-1 code.
#         locale – Specify the language of the query you are sending. This is intended for language-specific clients and the default should work in the majority of cases.
#         rpp – The number of tweets to return per page, up to a max of 100.
#         page – The page number (starting at 1) to return, up to a max of roughly 1500 results (based on rpp * page.
#         geocode – Returns tweets by users located within a given radius of the given latitude/longitude. The location is preferentially taking from the Geotagging API, but will fall back to their Twitter profile. The parameter value is specified by “latitide,longitude,radius”, where radius units must be specified as either “mi” (miles) or “km” (kilometers). Note that you cannot use the near operator via the API to geocode arbitrary locations; however you can use this geocode parameter to search near geocodes directly.
#         show_user – When true, prepends “<user>:” to the beginning of the tweet. This is useful for readers that do not display Atom’s author field. The default is false.
# 
#     Return type:    
# 
#     list of SearchResult objects

# In[90]:

api     = tweepy.API(auth)
results = api.search(q="IPython")


# Inspecting Results

# In[91]:

len(result)


# In[94]:

def print_tweet(tweet):
    print("@%s - %s (%s)" %(tweet.user.screen_name,tweet.user.name,tweet.created_at))
    print(tweet.text)

tweet = results[1]
print_tweet(tweet)


# In[95]:

Inspecting a Status Object


# In[96]:

tweet = result [2]

for param in dir(tweet):
    if not param.endswith("_",0,1):
        print ("%s : %s \n" %(param, eval("tweet." + param)))


# Inspecting a User Object

# In[99]:

tweet = result [1]
user = tweet.author

for param in dir(user):
    if not param.startswith("_"):
        print ("%s : %s" % (param, eval("user." + param)))


# Using Cursor for Pagination¶

# In[101]:

results = []
for tweet in tweepy.Cursor(api.search, q="IPython").items(100):
    results.append(tweet)

print (len(results))

Store Results in a Data Frame
# In[104]:


def process_results(results):
    id_list = [tweet.id for tweet in results]
    data_set = pd.DataFrame(id_list, columns=["id"])

    # Processing Tweet Data

    data_set["text"] = [tweet.text for tweet in results]
    data_set["created_at"] = [tweet.created_at for tweet in results]
    data_set["retweet_count"] = [tweet.retweet_count for tweet in results]
    data_set["favorite_count"] = [tweet.favorite_count for tweet in results]
    data_set["source"] = [tweet.source for tweet in results]

    # Processing User Data
    data_set["user_id"] = [tweet.author.id for tweet in results]
    data_set["user_screen_name"] = [tweet.author.screen_name for tweet in results]
    data_set["user_name"] = [tweet.author.name for tweet in results]
    data_set["user_created_at"] = [tweet.author.created_at for tweet in results]
    data_set["user_description"] = [tweet.author.description for tweet in results]
    data_set["user_followers_count"] = [tweet.author.followers_count for tweet in results]
    data_set["user_friends_count"] = [tweet.author.friends_count for tweet in results]
    data_set["user_location"] = [tweet.author.location for tweet in results]

    return data_set
data_set = process_results(results)


# In[ ]:

Looking at the Data


# In[105]:

data_set.head(5)


# Visualizing Results

# In[116]:

sources = data_set["source"].value_counts()[:5][::-1]

plt.barh(range(len(sources)), sources.values)
plt.yticks(np.arange(len(sources)) + 0.4, sources.index)
plt.show()


# ## Twitter Streaming

# Import libraries and Authentication

# In[3]:

import ipywidgets as wgt
from IPython.display import display
from sklearn.feature_extraction.text import CountVectorizer
import re
from datetime import datetime
import pymongo

get_ipython().magic('matplotlib inline')


# In[4]:

Consumer_Key    = 'jypioHVEm55HyWBOusZw1ICiM'
Consumer_Secret = 'vBjVAyJwQY1zKxCaTPYqqOgST7YLRhcTIvWcunTQFPUtCqTwYJ'
Access_Token    = '964193901115473920-mq6fZZJoVTo9VoytINW3GalpjgCmXvm'
Access_Token_Secret = 'G4T5I089sUvoMJ4OfQlkDxxsAdpn7Dv9ZRj074ITIH4fJ'
Owner_ID = 964193901115473920

auth = tweepy.OAuthHandler(Consumer_Key, Consumer_Secret)
auth.set_access_token(Access_Token, Access_Token_Secret)

api = tweepy.API(auth)


# In[1]:

MongoDB Collection
    Connect to MongoDB and create a collection


# In[6]:

col = pymongo.MongoClient()["tweets"]["StreamingTutorial"]
col.count()


# In[8]:

class MyStreamListener(tweepy.StreamListener):
    
    counter = 0
    
    def __init__(self, max_tweets=1000, *args, **kwargs):
        self.max_tweets = max_tweets
        self.counter = 0
        super().__init__(*args, **kwargs)
    
    def on_connect(self):
        self.counter = 0
        self.start_time = datetime.now()
    
    def on_status(self, status):
        # Increment counter
        self.counter += 1
        
        # Store tweet to MongoDB
        col.insert_one(status._json)
        
        
        if self.counter % 1 == 0:
            value = int(100.00 * self.counter / self.max_tweets)
            mining_time = datetime.now() - self.start_time
            progress_bar.value = value
            html_value = """<span class="label label-primary">Tweets/Sec: %.1f</span>""" % (self.counter / max([1,mining_time.seconds]))
            html_value += """ <span class="label label-success">Progress: %.1f%%</span>""" % (self.counter / self.max_tweets * 100.0)
            html_value += """ <span class="label label-info">ETA: %.1f Sec</span>""" % ((self.max_tweets - self.counter) / (self.counter / max([1,mining_time.seconds])))
            wgt_status.value = html_value
            #print("%s/%s" % (self.counter, self.max_tweets))
            if self.counter >= self.max_tweets:
                myStream.disconnect()
                print("Finished")
                print("Total Mining Time: %s" % (mining_time))
                print("Tweets/Sec: %.1f" % (self.max_tweets / mining_time.seconds))
                progress_bar.value = 0
                
    
myStreamListener = MyStreamListener(max_tweets=100)
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)


# In[9]:

keywords = ["Jupyter",
            "Python",
            "Data Mining",
            "Machine Learning",
            "Data Science",
            "Big Data",
            "DataMining",
            "MachineLearning",
            "DataScience",
            "BigData",
            "IoT",
            "#R",
           ]

# Visualize a progress bar to track progress
progress_bar = wgt.IntProgress(value=0)
display(progress_bar)
wgt_status = wgt.HTML(value="""<span class="label label-primary">Tweets/Sec: 0.0</span>""")
display(wgt_status)

# Start a filter with an error counter of 20
for error_counter in range(20):
    try:
        myStream.filter(track=keywords)
        print("Tweets collected: %s" % myStream.listener.counter)
        print("Total tweets in collection: %s" % col.count())
        break
    except:
        print("ERROR# %s" % (error_counter + 1))


# In[10]:

col.find_one()


# In[ ]:




# In[ ]:

class listener (StreamListener):
    def on_data(self,data):
        print (data)
        return True
    def on_error(self,status):
        print (status)

auth = tweepy.OAuthHandler(Consumer_Key, Consumer_Secret)
auth.set_access_token(Access_Token, Access_Token_Secret)
twitterStream = tweepy.Stream(auth, listener())
twitterStream.filter(track=["car"])
# api = tweepy.API(auth)

# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#     print (tweet.text)


# In[ ]:



