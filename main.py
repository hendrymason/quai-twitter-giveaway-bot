from xxlimited import new
from numpy import iterable
import tweepy
import csv
from typing import Iterable
import datetime
from datetime import timedelta

# Giveaway Rules:
# 1. Following @Quainetwork and Alanorwick -> check following
# 2. Like+retweet thread -> get likers+retweeters of tweets in thread
# 3. Join Discord -> ???
# 4. Tag 3 friends -> pull comments of thread tweets, check if comment has '@' symbol 3 times (counter loop on list(tweet.text)), and addt o tagged friends list


# quai twitter constants
quai_id = 1306071657174441985
alans_id = 516947335
giveaway_thread = [1496183164917665793, 1496183164917665793]
quai_username = 'quainetwork'
third_bearer = "" #coles
fourth_bearer = "" #owens
fifth_bearer = "" #maxs

# initialize client
client = tweepy.Client(bearer_token=fourth_bearer)

# 1. check if following @quainetwork and @alanorwick
alans_followers_resp = client.get_users_followers(id=alans_id, max_results=1000)
quais_followers_resp = client.get_users_followers(id=quai_id, max_results=1000)

alans_followers = []
quais_followers = []
def collect_users_followers(user_id):
    paginating = True
    next_token = ""
    while paginating == True:
        if next_token == "":
            users_followers = client.get_users_followers(id=user_id, max_results=1000)
        else:
            users_followers = client.get_users_followers(id=user_id, max_results=1000, pagination_token=next_token)
        
        for user in users_followers.data:
                if user_id == alans_id:
                    alans_followers.append(user.username)
                elif user_id == quai_id:
                    quais_followers.append(user.username)
        
        try:
            if users_followers.meta['next_token']:
                next_token = users_followers.meta['next_token']
        except:
            paginating = False

collect_users_followers(alans_id)
collect_users_followers(quai_id)
# create a list of users who follow BOTH alan and quai
following_accounts = [username for username in quais_followers if username in alans_followers]

#print("---- Total Accounts following Quai and Alan ----")
#print(len(following_accounts))

# 2. Check for users who liked+retweted the tweets in giveaway thread
# pull likers and retweeters list
def paginate(response, _id, user_type):
    pagination = True
    collected_data = []
    next_token = response.meta['next_token']
    pagination_count = 0
    while pagination == True:
        if user_type == "likes":
            new_response = client.get_liking_users(id=_id, pagination_token=next_token)
        elif user_type == "retweets":
            new_response = client.get_retweeters(id=_id, pagination_token=next_token)
        
        if new_response.data != None:
            for tweet_data in new_response.data:
                collected_data.append(tweet_data)
            pagination_count += 1
        else:
            print("pulled a 'None' Type for response")
        
        try:
            if new_response.meta["next_token"]:
                next_token = new_response.meta["next_token"]
        except:
            print("done paginating")
            print("paginated " + user_type + " " + str(pagination_count) + " times.")
            pagination = False
    
    return collected_data

for tweet_id in giveaway_thread:
    likers_list = []
    retweeters_list = []

    likers_response = client.get_liking_users(tweet_id)
    retweeters_response = client.get_retweeters(tweet_id)

    likers_data = likers_response.data
    retweeters_data = retweeters_response.data

    try:
        if likers_response.meta['next_token']:
            paginated_data = paginate(likers_response, tweet_id, "likes")
            for data in paginated_data:
                likers_data.append(data)
    except:
        print("likers_response did not need to be paginated")

    try:
        if retweeters_response.meta['next_token']:
            paginated_data = paginate(retweeters_response, tweet_id, "retweets")
            for data in paginated_data:
                retweeters_data.append(data)
    except:
        print("retweeters_response list did not need to be paginated")

    # pull username into liker list from likers data
    if isinstance(likers_data, Iterable):
        for liker in likers_data:
            if liker.username not in likers_list:
                likers_list.append(liker.username)
    # pull username into retweeter list from retweeters data 
    if isinstance(retweeters_data, Iterable):
        for retweeter in retweeters_data:
            if retweeter.username not in retweeters_list:
                retweeters_list.append(retweeter.username)
            
# create new list of users who liked AND retweeted the tweets
liked_retweeted = [username for username in likers_list if username in retweeters_list]
#print("---- Total Accounts Liked+Retweeted Giveaway Tweets ----")
#print(len(liked_retweeted))
#print(liked_retweeted)

almost_qualified = [username for username in liked_retweeted if username in following_accounts]

users_to_request = []
users_list = []
users_count = 0
total_user_count = 0
qualified_count = len(almost_qualified)
for user in almost_qualified:
    if users_count < 100:
        users_list.append(user)
        users_count += 1
        total_user_count += 1
    else:
        users_to_request.append(users_list)
        users_list = []
        users_count = 0
        users_list.append(user)
        users_count += 1
        total_user_count += 1
    
    if total_user_count == qualified_count:
        users_to_request.append(users_list)

#print(users_to_request)
#print(len(users_to_request))

print(" --- done with adding to users_to_request --- ")
#print("--- users_to_request --- ")
#print(users_to_request)
user_data = {}
reversed_user_data = {}
for user_list in users_to_request:
    users_response = client.get_users(usernames=user_list)
    for account in users_response.data:
        user_data[account.username] = account.id
        reversed_user_data[account.id] = account.username
#print(" --- user_data --- ")
#print(user_data)

# 4. Check for 3 tagged users in reply tweets

tweet = client.get_tweet(id=1496183164917665793, tweet_fields='created_at')
giveaway_datetime = tweet.data['created_at']
replies = {}
for username in almost_qualified:
    if username in user_data.keys():
        user_id = user_data[username]
        
        indiv_tweets = client.get_users_tweets(id=user_id, exclude=['retweets', 'replies'], start_time = giveaway_datetime, tweet_fields=['created_at', 'conversation_id', 'author_id', 'text'], max_results=100)
        no_retweets = client.get_users_tweets(id=user_id, exclude='retweets', start_time = giveaway_datetime, expansions='entities.mentions.username', tweet_fields=['created_at', 'conversation_id', 'author_id', 'text'], max_results=100)
        
        indiv_tweets_list = []
        if isinstance(indiv_tweets.data, Iterable):
            for tweet in indiv_tweets.data:
                indiv_tweets_list.append(tweet.id)

        #sort tweets to get just the user reply tweets on the giveaway thread
        if isinstance(no_retweets.data, Iterable):
            #print("reading retweets")
            for tweet in no_retweets.data:
                #print("reading individual tweets")
                if tweet.id not in indiv_tweets_list and tweet.conversation_id in giveaway_thread:
                    if user_id not in replies.keys():
                        replies[user_id] = tweet.text
#print(replies)
tagged_3 = []
for user_id in replies.keys():
    mention_count = 0
    tweet_text = list(replies[user_id])
    for text in tweet_text:
        if '@' in text:
            mention_count += 1
    if mention_count >= 3:
        if user_id in user_data.values():
            tagged_3.append(reversed_user_data[user_id])
#print(tagged_3)

# Aggregate total users who qualify for giveaway
qualified_users = [username for username in almost_qualified if username in tagged_3]

#print(" -- almost qualified -- ")
#print(almost_qualified)
#print(" -- qualified users -- ")
#print(qualified_users)
