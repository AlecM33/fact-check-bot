import json
import praw
from os import environ
from googleapiclient.discovery import build
import os

api_key = os.environ['API_KEY']
client_id = os.environ['REDDIT_CLIENT_ID']
secret = os.environ['REDDIT_SECRET']
password = os.environ['REDDIT_PW']
username = os.environ['BOT_USERNAME']

reddit = praw.Reddit(client_id=client_id,
                     client_secret=secret,
                     password=password,
                     user_agent='fact check bot by /u/alecm33',
                     username=username)

factCheckService = build("factchecktools", "v1alpha1", developerKey=api_key)

sub = reddit.subreddit('CHANGEME')

#TODO add validations for API response
def buildMessage(res):
    claim = res["claims"][0]
    publisher = claim["claimReview"][0]["publisher"]["name"]
    rating = claim["claimReview"][0]["textualRating"]
    url = claim["claimReview"][0]["url"]
    claimText = claim["text"]
    return "According to **" + publisher + "**, the claim _" + claimText + "_ is **" + rating + "**.\n\nFull source: <" + url +">\n\n^I ^am ^a ^bot ^utilizing ^Google's ^fact ^check ^exploration ^tool."

for comment in politicsSub.stream.comments():
    if comment.body.lower().find("!factcheck") != -1:
        userQuery = comment.body.lower().split("!factcheck")[1].strip(" ")
        request = factCheckService.claims().search(query=userQuery)
        response = request.execute()
        reply = buildMessage(response)
        comment.reply(reply)