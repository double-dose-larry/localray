from env import * # holds all the secrets
import praw
from ray import Ray
from flappy_answers import answers
import random
import os
# set up a praw instance to use as a listener
# let's listen to all comments on r/tampabayrays and highlight those that have the word cash in them
#works
ray = Ray()

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
            comment.reply(respond(comment))
            replied.append(comment.id)
        with open('replied.txt','w') as f:
            f.writelines([f"{x}\n" for x in replied])
        # fire off the make decision function, pass comment




