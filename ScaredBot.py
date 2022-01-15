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
verbs = {x.name().split('.', 1)[0] for x in wn.all_synsets('v')}
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
    excludedWords = ["my", "the", "is", "i", "I"]
    #forbiddenWords: words to skip over
    forbiddenWords = ["lol", "LOL", "lmao", "LMAO", "wtf", "omg", "is", "nigga","niggas"]
    
    #scrub data
    tweets = data[0]
    
    leastTweeted = 0
    try:
        for i in tweets:
            print(i.text)
            if(i.text.find("im scared of")!= -1):
                removePunc = re.split('[.?!\s]',i.text[i.text.find("im scared of")+13:])
                if len(removePunc) == 0: 
                    continue
                try:
                    while True:
                        removePunc.remove('')
                except ValueError:
                    pass
                
                word = ""
                count = 0
                print(removePunc)
                if len(removePunc)>1:
                    while(count<len(removePunc) and (removePunc[count] not in nouns and removePunc[count] not in excludedWords)):
                        if(removePunc[count][-1]=="s" and removePunc[count][:-1] not in excludedWords and removePunc[count][:-1] in nouns): #check if nonplural form is recognized
                            word += removePunc[count]
                            break
                        elif removePunc[count] not in forbiddenWords:
                            word += removePunc[count]+" "
                            count += 1
                            continue
                        count+=1 #count up here in case it hits a forbidden word
                    else:
                        while((count < len(removePunc) and removePunc[count] in nouns) or (len(word)>1 and len(word.split(" ")[-2]) == 1)):#test ruleset, in case of phrases like "i'm scared of losing someone I love"
                            if(count>=len(removePunc)):
                                break
                            word += removePunc[count] + " "
                            count+=1
                            if(count+1 <len(removePunc) and removePunc[count+1][-1]=="s" and removePunc[count+1][:-1] not in excludedWords and removePunc[count+1][:-1] in nouns): #check if nonplural form is recognized
                                word += removePunc[count]
                            if(count+1 <len(removePunc) and removePunc[count] == "being"):
                                word += removePunc[count+1]
                    if("https" in word ): #if has link, omit
                        word = ""
                elif len(removePunc)>0:
                    word = removePunc[0]
                print("tweet ID: ",i.id)
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
                removePunc = re.split('[.?!\s]',i.text[i.text.find("im scared of")+13:])
                if len(removePunc) == 0: 
                    continue
                try:
                    while True:
                        removePunc.remove('')
                except ValueError:
                    pass
                
                word=""
                count = 0
                print(removePunc)
                if len(removePunc)>1:
                    while(count<len(removePunc) and (removePunc[count] not in nouns and removePunc[count] not in excludedWords)):
                        if(removePunc[count][-1]=="s" and removePunc[count][:-1] not in excludedWords and removePunc[count][:-1] in nouns): #check if nonplural form is recognized
                            word += removePunc[count]
                            break
                        elif removePunc[count] not in forbiddenWords:
                            word += removePunc[count]+" "
                            count += 1
                            continue
                        count+=1 #count up here in case it hits a forbidden word
                    else:
                        while((count < len(removePunc) and removePunc[count] in nouns) or (len(word)>1 and len(word.split(" ")[-2]) == 1)):#test ruleset, in case of phrases like "i'm scared of losing someone I love"
                            if(count>=len(removePunc)):
                                break
                            word += removePunc[count] + " "
                            count+=1
                            if(count+1 <len(removePunc) and removePunc[count+1][-1]=="s" and removePunc[count+1][:-1] not in excludedWords and removePunc[count+1][:-1] in nouns): #check if nonplural form is recognized
                                word += removePunc[count]
                            if(count+1 <len(removePunc) and removePunc[count] == "being"):
                                word += removePunc[count+1]
                    if("https" in word ): #if has link, omit
                        word = ""
                else:
                    word = removePunc[0]
                print("tweet ID: ",i.id)
                print(word)
                print(storage.get(word))
                print("---")
                if(len(word.split(" "))>10): #if the phrase is longer than 10 words, move on
                    word = ""
                
                if storage.get(word, None) == None:
                    if leastTweeted == 0 and text == "": #replace tweeted word if its first scanned and no record of it
                        text = word
                    elif leastTweeted > 0 and storage.get(word, None)<leastTweeted: #replace tweeted word if is the first scanned word that is new
                        text = word
                elif storage.get(word, None) < leastTweeted: #replace tweeted word if searched word is used less than others scanned in batch
                    text = word
                    leastTweeted = storage.get(word)
    except:
        print("ERROR")            
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
    # getText(results) #dev
    
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

