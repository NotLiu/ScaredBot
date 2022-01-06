import os
import tweepy
import json
import string
import re
import schedule
import time
from nltk.corpus import wordnet as wn
from nltk.corpus import words
from dotenv import load_dotenv

#all nouns from nltk.corpus
nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
storage = dict()

load_dotenv()
apiKey = os.getenv("API_KEY") #consumer key
apiKeySecret = os.getenv("API_KEY_SECRET")
accessToken = os.getenv("ACCESS_TOKEN") #access key
accessTokenSecret = os.getenv("TOKEN_SECRET")
bearerToken = os.getenv("BEARER_TOKEN")

client = tweepy.Client(bearer_token=bearerToken,
                       consumer_key=apiKey,
                       consumer_secret=apiKeySecret,
                       access_token=accessToken,
                       access_token_secret=accessTokenSecret)

def createTweet(tweet):
    response = client.create_tweet(text=tweet)
    print("TWEET CREATED")
    print("===========================================")
    print(response)
    print("===========================================")
    writeStorage()

def scaredSearch():
    query='"im scared of"'
    response = client.search_recent_tweets(query=query, max_results = 10)
    return response
    
def getText(data):
    global storage
    scared = "I'm scared"
    interText = ".."
    text = ""
    
    #excludedWords: words that dont make sense alone
    excludedWords = ["my", "the"]
    #forbiddenWords: words to skip over
    forbiddenWords = ["lol", "LOL", "lmao", "LMAO", "wtf", "omg"]
    
    #scrub data
    tweets = data[0]
    
    leastTweeted = 0
    for i in tweets:
        print(i.id)
        if(i.text.find("im scared of")!= -1):
            r = re.compile(r'[\s{}]+'.format(re.escape(string.punctuation)))
            removePunc = r.split(i.text[i.text.find("im scared of")+13:])
            
            word = ""
            count = 0
            if len(removePunc)>1:
                while(count<len(removePunc)-1 and ((removePunc[count] not in nouns and removePunc[count] not in excludedWords) or (count+1<len(removePunc) and removePunc[count+1] in nouns))):
                    if(removePunc[count][-1]=="s" and removePunc[count][:-1] not in excludedWords and removePunc[count][:-1] in nouns): #check if nonplural form is recognized
                        word += removePunc[count]
                        break
                    elif removePunc[count] not in forbiddenWords:
                        word += removePunc[count]+" "
                        count += 1
                        continue
                    count+=1 #count up here in case it hits a forbidden word
                else:
                    word += removePunc[count]
                if(removePunc[-1] not in words.words() and (len(removePunc)>1 and removePunc[-2] not in words.words())): #if last word is not a word, omit
                    word = ""
            else:
                word = removePunc[0]
            print(word)
            print(storage.get(word))
            print("---")
            if(len(word.split(" "))>10): #if the phrase is longer than 10 words, move on
                word = ""
            if storage.get(word, None) == None:
                if leastTweeted == 0 and text == "": #replace tweeted word if its first scanned and no record of it
                    text = word
                elif leastTweeted > 0 and storage.get(text,1)>leastTweeted: #replace tweeted word if is the first scanned word that is new
                    text = word
            elif int(storage.get(word, None)) < leastTweeted: #replace tweeted word if searched word is used less than others scanned in batch
                text = word
                leastTweeted = storage.get(word)
        else:
            r = re.compile(r'[\s{}]+'.format(re.escape(string.punctuation)))
            removePunc = r.split(i.text[i.text.find("im scared of")+13:])
            
            if (removePunc[0] in excludedWords):
                word = removePunc[0]+" "+removePunc[1]
            else:
                word = removePunc[0]
            
            if storage.get(word, None) == None:
                if leastTweeted == 0 and text == "": #replace tweeted word if its first scanned and no record of it
                    text = word
                elif leastTweeted > 0 and storage.get(word, None)<leastTweeted: #replace tweeted word if is the first scanned word that is new
                    text = word
            elif storage.get(word, None) < leastTweeted: #replace tweeted word if searched word is used less than others scanned in batch
                text = word
                leastTweeted = storage.get(word)
                
    print("===========================================")
    print("The newest word is: " + text)
    
    if text != "":
        interText = " of "
    elif len(text).split() == 1:
        interText = " of the letter "
    
    tweet = scared + interText + text + ".."
    print("===========================================")
    print("TWEETING: " + tweet)
    print("===========================================")
    print("STORING WORD")
    print("===========================================")
    store(text)
    return tweet
    
def readStorage():
    global storage
    file = open("storage.json", "r")
    storage = json.load(file)
    print("STORAGE READ")
    print("===========================================")
    print(storage)
    print("===========================================")
    file.close()
    
def writeStorage():
    global storage
    file = open("storage.json", "w")
    json.dump(storage,file)
    file.close()
    
def store(item):
    global storage
    if(storage.get(item,None)==None):
        storage[item] = 1
    else:
        storage[item] = storage[item]+1

def main():
    readStorage()
    print("===========================================")
    print("SEARCHING")
    print("===========================================")
    results = scaredSearch()
    
    createTweet(getText(results))
    print("RUN COMPLETED")
    print("*******************")
    print("SLEEPING")
    print("*******************")

main()
schedule.every(30).minutes.do(main)
    
while True:
    schedule.run_pending()
    time.sleep(1)

