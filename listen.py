from env import * # holds all the secrets
import praw
from ray import Ray
from flappy_answers import answers
import json
import random
import os
import requests
import re
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

# set up a praw instance to use as a listener
# let's listen to all comments on r/tampabayrays and highlight those that have the word cash in them
#works
ray = Ray()

def create_wordcloud(url):
    print("in create_wordlcoud")
    post = reddit.submission(url=url)
    gdt_thread_comments = post.comments.list()
    title = "Wordcloud for " + post.title
    print(title)
    wc = WordCloud(background_color="white", 
               max_words=200,
               width=1080,
               height=720,
               stopwords=STOPWORDS, 
               contour_width=3, 
               contour_color='steelblue',
               font_path="font.ttf")
    print("generating wordcloud")
    text = ' '.join([ x.body for x in gdt_thread_comments])
    text = text.replace("_","").replace("\n","").replace("\\", "").replace("∩","").replace("≡","").replace("  ","").replace("~","").replace("/","").replace("‖","")
    wc.generate(text)
    wc_file = f"{post.created_utc}_cloud.png"
    wc.to_file(wc_file)

    print("file created. uploading to imgur") 
    imgur_client_id = 'dd6f501b4b49c74'
    url = "https://api.imgur.com/3/image"
    with open(wc_file, 'rb') as f:
        payload = {
            'image': f.read(),
            'title': title,
            'description': f"https://np.reddit.com{post.permalink}"
        }
    headers = {
       'Authorization': f'Client-ID {imgur_client_id}'
       }
    response = requests.post(url,headers=headers,data=payload)
    if response.status_code == 200:
        return json.loads(response.text)["data"]["link"]


def respond(comment):
    if '?' in comment.body:
        return ray.raysay(random.choice(answers))
    elif 'info' in comment.body:
        return ray.raysay("""
You can:
Ask me a yes/no question? (ex: "localray are we going to win?").
Ask for this info with "localray info".
that's it for now, but many more abilities to come... hopefully.

Otherwise I'll respond with a flappy quote. :)
""")
    elif 'wordcloud' in comment.body:
        print("starting wordcloud")
        try:
            url = re.search("(?P<url>https?://[^\s]+)", comment.body).group("url")
            if 'reddit' in url:
                return ray.raysay(f"Tring to create a wordcloud for {url}")
        except Exception as e:
            #raise e
            return ray.raysay(f"Couldn't do it this time, but here's a piece of advice", quote=True)
        
    else:
        return ray.raysay("I'm not sure, but here's a quote that may shed some insight",quote=True)

reddit = praw.Reddit(user_agent=RAY_USER_AGENT,
                     client_id=RAY_CLIENT_ID,
                     client_secret=RAY_SECRET,
                     username=RAY_USERNAME,
                     password=RAY_PASSWORD)
                     
tb = reddit.subreddit('tampabayrays')

# stream comments, print new comments on screen and do something special if comment has 'cash'

with open('replied.txt', 'r') as f:
    replied = f.read().splitlines()


for comment in tb.stream.comments():
    print(comment.parent_id, comment.author, "says", comment.body)
    if 'localray' in comment.body.lower() and comment.author != 'localray':
        print ("*"*20,"\nlocalray is here to answer your questions\n","*"*20)
        if comment.id not in replied:
            print("new comment")
            reply = comment.reply(respond(comment))
            if 'wordcloud' in reply.body:
                final_url = re.search("(?P<url>https?://[^\s]+)", comment.body).group("url")
                reply.reply(f"[Here is the worldcloud for that post's comments]({create_wordcloud(final_url)})")
                final_url = None
            replied.append(comment.id)
        with open('replied.txt','w') as f:
            f.writelines([f"{x}\n" for x in replied])
        # fire off the make decision function, pass comment




