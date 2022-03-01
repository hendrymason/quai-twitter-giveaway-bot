import tweepy
import csv
from typing import Iterable

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
third_bearer = "AAAAAAAAAAAAAAAAAAAAAJlpZQEAAAAAjwv7Gg01zTG7ck30cyqxiwQcm9U%3DPNHl3UjpTpKdAjtVcrOs8tZqprtwO6TUKl61XWrXzKKVwgkMDA" #coles
fourth_bearer = "AAAAAAAAAAAAAAAAAAAAAJxpZQEAAAAAexanqSH%2B10AH6FDOHTOqAlqiI8g%3D9hHfSUY0qNXjDGBwlBRNqhXelDcDYpNvnW4VGtpiroOAlabxaR" #owens

# initialize client
client = tweepy.Client(bearer_token=third_bearer)

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

print("---- Total Accounts following Quai and Alan ----")
print(len(following_accounts))

#def paginate(response, _method, _id, _field _field_value):
def paginate(response, _id, type):
    pagination = True
    collected_data = []
    while pagination == True:
        next_token = response.meta['next_token']
        if type == "likes":
            new_response = client.get_liking_users(id=_id)
        elif type == "retweets":
            new_response = client.get_retweeters(id=_id)
        collected_data.append(new_response.data)
        try:
            if new_response.meta["next_token"]:
                new_token = new_response.meta["next_token"]
        except:
            print("done paginating")
            pagination = False
    return collected_data


# 2. Check for users who liked+retweted the tweets in giveaway thread
# pull likers and retweeters list
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
            likers_data.append(paginated_data)
    except:
        print("likers_response did not need to be paginated")

    try:
        if retweeters_response.meta['next_token']:
            paginated_data = paginate(retweeters_response, tweet_id, "retweets")
            retweeters_data.append(paginated_data)
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
print("---- Total Accounts Liked+Retweeted Giveaway Tweets ----")
print(len(liked_retweeted))
print(liked_retweeted)


# 4. Check for 3 tagged users in reply tweets
replies = {}
for tweet_id in giveaway_thread:
    
    tweet_replies = client.search_recent_tweets(query="conversation_id:" + str(tweet_id), tweet_fields=['author_id','text'], max_results=100)
    
    for tweet in tweet_replies.data:
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if tweet.id not in replies.keys():
                replies[tweet.id] = [tweet.author_id, tweet.text]

tagged_3 = []
for reply_id in replies.keys():
    tweet_text_list = list(replies[reply_id][1])
    count = 0
    for word in tweet_text_list:
        if '@' in word:
            count += 1
    if count >= 3:
        tagged_3.append(replies[reply_id][0])

# Aggregate total users who qualify for giveaway
qualified_users = [username for username in following_accounts if (username in liked_retweeted and username in tagged_3)]

print(qualified_users)

