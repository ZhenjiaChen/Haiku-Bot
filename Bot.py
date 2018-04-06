import string
import praw
import config
import os
import time
import urllib.request as url2
from bs4 import BeautifulSoup

with open('dictionary.txt', 'r') as f:
    syllable_dictionary = eval("{" + f.read() + "}")

def bot_login():
    reddit = praw.Reddit(username = config.username,
                         password = config.password,
                         client_id = config.client_id,
                         client_secret = config.client_secret,
                         user_agent = "User Agent")
    return reddit

def run_bot(r, comment_list):
    for comment in r.subreddit("all").comments(limit=25):
        if len(comment.body.split()) <= 17 :
            if not comment.id in comment_list and comment.author != r.user.me():
                if is_haiku(comment.body):
                    print("---Haiku found, making poem!---")
                    haiku = make_haiku(comment.body)
                    if comment.body.count('\n') >= 2:
                        print("---Aw...original comment might already be a haiku!---")
                    else:
                        comment.reply(haiku)
                        print("---Replied and now...---")
                    print("---...Remembering comment id!---")
                    with open("comments_replied_to.txt", "a") as f:
                        f.write(comment.id + "\n")
                    print("---Sleeping...---")
                    time.sleep(60)
                else:
                    print("---Not a haiku!---")
            else:
                print("---Already replied to or it is me!---")
        else:
            print("---Comment longer than 17 words!---")
    print("---Sweep done, now sleeping!---")
    time.sleep(10)

def memorize(word, syllable):
    with open("dictionary.txt", "a") as f:
        f.write('"%s" : %s,\n' % (word, syllable))
    with open("dictionary.txt", "r") as f:
        return eval("{" + f.read() + "}")

def get_saved_comments():
    if not os.path.isfile("comments_replied_to.txt"):
        comments_replied_to = []
    else:
        with open("comments_replied_to.txt", "r") as f:
            comments_replied_to = f.read()
            comments_replied_to = comments_replied_to.split("\n")
            comments_replied_to = filter(None, comments_replied_to)

    return comments_replied_to

def test(comment):
    if len(comment.split()) <= 17 :
        if is_haiku(comment):
            haiku = make_haiku(comment)
            print(comment)
            if comment.count('\n') == 2:
                print("Already a haiku")
            else:
                print('Replied with:\n' + haiku)

def syllables(word):
    global syllable_dictionary
    punctuation = string.punctuation[0:6] + string.punctuation[7:]
    lower = word.replace(u"\u2019", "'").replace(u"\u2018", "'").translate(str.maketrans("","", string.punctuation)).lower()

    try:
        if lower in syllable_dictionary.keys():
            syllables = syllable_dictionary.get(lower)
            print(word + ' : ' + str(syllables) + " ---Got from memory!---")
            return syllables
        else:
            url = "https://www.howmanysyllables.com/words/" + lower
            page = url2.urlopen(url)
            soup = BeautifulSoup(page, 'html.parser')
            
            
            style = soup.findAll('style')
            for entry in style:
                if '#abxy' in str(entry):
                    index = style.index(entry)
    
            word_id = style[index].text[1:8]
            header = soup.find('h1')
    
            if lower == header.text.lower():
                syllables = soup.find('span', attrs={'id': word_id}).text
                print(word + ' : ' + syllables)
                syllable_dictionary = memorize(lower, syllables)
                return int(syllables)
            else:
                print("Word did not match one found in dictionary: " + word)
                return None

    except:
            print("Did not find word in dictionary: " + word)
            return None

def is_haiku(comment):
    syllable_count = 0
    mark1 = False
    mark2 = False
    mark3 = False
    if len(comment.split()) > 17:
        return False
    else:
        try:
            for word in comment.split():
                syllable_count += syllables(word)
                if syllable_count == 5:
                    mark1 = True
                elif syllable_count > 5 and not mark1:
                    return False
                elif syllable_count == 12:
                    mark2 = True
                elif syllable_count > 12 and not mark2:
                    return False
                elif syllable_count == 17:
                    mark3 = True
                elif syllable_count > 17:
                    return False
            return mark1 and mark2 and mark3
        except TypeError:
            return False

def make_haiku(haiku):
    line1 = ''
    line2 = ''
    line3 = ''
    syllable_count = 0
    originalcase = haiku.split()
    lowercase = haiku.translate(str.maketrans("","", string.punctuation)).lower().split()

    for i in range(len(lowercase)):
        syllable_count += syllables(lowercase[i])
        if syllable_count <= 5:
            if len(line1) == 0:
                line1 += originalcase[i].capitalize() + " "
            else:
                line1 += originalcase[i] + " "
        elif syllable_count <= 12:
            if len(line2) == 0:
                line2 += originalcase[i].capitalize() + " "
            else:
                line2 += originalcase[i] + " "
        elif syllable_count <= 17:
            if len(line3) == 0:
                line3 += originalcase[i].capitalize() + " "
            else:
                line3 += originalcase[i] + " "
    return line1 + "\n\n" + line2 + "\n\n" + line3

reddit = bot_login()
comments_replied_to = get_saved_comments()

while True:
    run_bot(reddit, comments_replied_to)
