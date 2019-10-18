from env import * # holds all the secrets
import praw
from ray import Ray
import requests
import pandas as pd
import time
# set up a praw instance to use as a listener
# let's listen to all comments on r/tampabayrays and highlight those that have the word cash in them
#works
ray = Ray()

reddit = praw.Reddit(user_agent=RAY_USER_AGENT,
                     client_id=RAY_CLIENT_ID,
                     client_secret=RAY_SECRET,
                     username=RAY_USERNAME,
                     password=RAY_PASSWORD)


# MUST HAVE THESE VALUES BE CORRECT FOR EACH GAME
game_url = "https://www.fangraphs.com/api/play-log/live-results?dateGame=2019-10-10&teamid=12&dh=0" # exmaple: 'https://www.fangraphs.com/api/play-log/past-results?dateGame=2019-09-03&teamid=12&dh=1'
gdt_url = "https://www.reddit.com/r/tampabayrays/comments/dfwyra/game_chat_1010_alds_game_5_rays_2_astros_2_707_pm/"# example: 'https://www.reddit.com/r/tampabayrays/comments/czzuhe/game_chat_95_blue_jays_5585_rays_8259_710_pm/'
gdt_thread = reddit.submission(url=f"{gdt_url}")
# starting values
last_we = .5 
last_df = pd.DataFrame() 
reply_que = []

# set up a loop that polls every 20 seconds

while True:
    seconds_to_wait = 20
    print(f"looping every {seconds_to_wait} seconds")
    try:
        json_data = requests.get(game_url).content
        df = pd.read_json(json_data)
    except Exception as e:
        print(e)
        pass
    try:
        new_rows = df.merge(last_df,how='outer',indicator=True).loc[lambda x: x['_merge']=='left_only']
    except pd.errors.MergeError:
        new_rows = df

    print(new_rows.shape[0], " new events retreived")
    for row in new_rows.itertuples():
        we=1-row.we
        if we - last_we > .15:
            print(row.playDesc,last_we,we)
            reply_que.append(ray.raysay(f"{row.playDesc}\n Woo!! our chances of winning are now {we:.2%}"))
            last_we = we
        if we - last_we < -.15:
            print(row.playDesc,last_we,we)
            reply_que.append(ray.raysay(f"{row.playDesc}\n Oh No!! our chances of winning are now {we:.2%}"))
            last_we =we
    if len(reply_que) > 0:
        next_reply = reply_que.pop(0)
        print(next_reply)
        gdt_thread.reply(next_reply)
    last_df = df
    time.sleep(seconds_to_wait)
    
