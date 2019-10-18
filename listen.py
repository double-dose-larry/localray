from env import * # holds all the secrets
import praw
from ray import Ray
from flappy_answers import answers
import json
import random
import os
import requests
import re
import datetime
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

STOPWORDS.add("game")
STOPWORDS.add("deleted")
STOPWORDS.add("fuck")
STOPWORDS.add("fucking")
STOPWORDS.add("localray")
STOPWORDS.add("https")
STOPWORDS.add("reddit")
STOPWORDS.add("create")
STOPWORDS.add("wordcloud")
STOPWORDS.add("commets")
STOPWORDS.add("imgur")
# set up a praw instance to use as a listener
# let's listen to all comments on r/tampabayrays and highlight those that have the word cash in them
#works
ray = Ray()

def create_wordcloud(url):
    print("in create_wordlcoud")
    post = reddit.submission(url=url)
    post.comments.replace_more()
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
    print(f"generating wordcloud using {len(gdt_thread_comments)}")
    text = ' '.join([ x.body for x in gdt_thread_comments if not isinstance(x,praw.models.MoreComments)])
    text = text.replace("_","").replace("\n","").replace("\\", "").replace("∩","").replace("≡","").replace("  ","").replace("~","").replace("‖","")
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
    elif 'wordcloud' in comment.body.lower():
        print("starting wordcloud")
        try:
            url = re.search("(?P<url>https?://[^\s]+)", comment.body).group("url")
            if 'reddit' in url:
                return ray.raysay(f"Trying to create a wordcloud for {url}")
        except Exception as e:
            #raise e
            return ray.raysay(f"Couldn't do it this time, but here's a piece of advice", quote=True)
    elif '🍝' in comment.body:
        return ray.raysay("I still don't understand how this Rays team is in a playoff position. They're not as good of a team as Oakland or Cleveland. Their lineup is a joke, they look like a 1970s offense in an era where power pitching and power hitting reigns supreme. They scored TWO runs in 12 innings against the likes of Tarpley, Cessa, Lyons, Gearrin, and Montgomery who just returned from TJS? Their pitching staff is literally just Morton and a bunch of middle relief guys that somehow string together game after game. Combine that with their home ballpark, they are the definition of boring. I don't want this team in the playoffs because they're just so unlikable. At least Cleveland and Oakland have real talent.", length=100)
    elif 'balk' in comment.body.lower():
        return ray.raysay("""Balk Rules

You can't just be up there and just doin' a balk like that.

1a. A balk is when you

1b. Okay well listen. A balk is when you balk the

1c. Let me start over

1c-a. The pitcher is not allowed to do a motion to the, uh, batter, that prohibits the batter from doing, you know, just trying to hit the ball. You can't do that.

1c-b. Once the pitcher is in the stretch, he can't be over here and say to the runner, like, "I'm gonna get ya! I'm gonna tag you out! You better watch your butt!" and then just be like he didn't even do that.

1c-b(1). Like, if you're about to pitch and then don't pitch, you have to still pitch. You cannot not pitch. Does that make any sense?

1c-b(2). You gotta be, throwing motion of the ball, and then, until you just throw it.

1c-b(2)-a. Okay, well, you can have the ball up here, like this, but then there's the balk you gotta think about.

1c-b(2)-b. Fairuza Balk hasn't been in any movies in forever. I hope she wasn't typecast as that racist lady in American History X.

1c-b(2)-b(i). Oh wait, she was in The Waterboy too! That would be even worse.

1c-b(2)-b(ii). "get in mah bellah" -- Adam Water, "The Waterboy." Haha, classic...

1c-b(3). Okay seriously though. A balk is when the pitcher makes a movement that, as determined by, when you do a move involving the baseball and field of

Do not do a balk please""", length=80)
    elif 'cash' in comment.body.lower():
        return ray.raysay("Oakland, Boston, New York, Cleveland, one other club. Were we good enough? You're goddamn right we are. Let's fucking do this! -- Kevin Cash")
    elif 'countdown' in comment.body.lower():
        return ray.raysay(f"Rays 2020 season starts on March 26th, {(datetime.date(2020,3,26) - datetime.date.today()).days} days away.")
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
    if '!localray' in comment.body.lower() and comment.author != 'localray':
        print ("*"*20,"\nlocalray is here to answer your questions\n","*"*20)
        if comment.id not in replied:
            print("new comment")
            reply = comment.reply(respond(comment))
            if 'wordcloud' in reply.body:
                final_url = re.search("(?P<url>https?://[^\s]+)", comment.body).group("url")
                try:

                    reply.reply(f"[Here is the worldcloud for that post's comments]({create_wordcloud(final_url)})")

                except Exception as e:
            #raise e
                   reply.reply(ray.raysay(f"Couldn't do it this time, but here's a piece of advice", quote=True))

                final_url = None
            replied.append(comment.id)
        with open('replied.txt','w') as f:
            f.writelines([f"{x}\n" for x in replied])
        # fire off the make decision function, pass comment




