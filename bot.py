import json
import praw
from os import environ
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

api_key = os.environ['API_KEY']
client_id = os.environ['REDDIT_CLIENT_ID']
secret = os.environ['REDDIT_SECRET']
password = os.environ['REDDIT_PW']
username = os.environ['BOT_USERNAME']

reddit = praw.Reddit(client_id=client_id,
                     client_secret=secret,
                     password=password,
                     user_agent='Fact-Check-Bot v 1.0.0 by /u/alecm33',
                     username=username)

MAX_CLAIMS = 3
EMPTY_QUERY_ERROR = "You did not provide a query from which to filter claims!\n\n"
API_ERROR = "There was an issue with fetching claims for your query. :( You could try again another time."
replyHeader = "Attempting to curate up to 3 relevant fact-checked claims based on your query. Irrelevant? Try being more specific.\n\n"
replyFooter = "\n\n_I am a bot utilizing Google's fact check exploration tool. I currently monitor r/politics, r/news, r/worldnews, r/Liberal, and r/Conservative (banned)._ \n\n^[Code/Documentation](https://github.com/AlecM33/fact-check-bot)"

def main():
    # monitor comment streams for relevant subreddits
    for comment in reddit.subreddit("politics+news+worldnews+Liberal+Conservative").stream.comments(skip_existing=True):
        if comment.body.lower().find("!factcheck") != -1:
            userQuery = comment.body.lower().split("!factcheck")[1].strip(" ")
            if (len(userQuery) == 0):
                try:
                    comment.reply(EMPTY_QUERY_ERROR + replyFooter)
                except praw.exceptions.APIException as e:
                    continue
            else:
                try:
                    # attemt call to Google's fact check API 
                    factCheckService = build("factchecktools", "v1alpha1", developerKey=api_key)
                    request = factCheckService.claims().search(query=userQuery)
                    response = request.execute()
                # TODO more specifically handle problems with Google's API
                except HttpError as err:
                    try:
                        comment.reply(API_ERROR + replyFooter)
                    except praw.exceptions.APIException as e:
                        continue
                else:
                    reply = buildMessage(response)
                    try:
                        comment.reply(reply)
                    except praw.exceptions.APIException as e:
                        print ("Possibly rate limited!")
                        continue

def buildTableRow(claim):
    review = claim["claimReview"][0]
    publisher = ""
    rating = ""
    url = ""
    claimText = ""
    # make sure keys are present, since API documentation is uncertain
    if ("publisher" in review):
        publisher = review["publisher"]["name"]
    if ("textualRating" in review):
        rating = review["textualRating"]
    if ("url" in review):
        url = review["url"]
    if ("text" in claim):
        claimText = claim["text"]
    return "| _" + claimText + "_ | **" + rating + "** | " + "[" + publisher + "](" + url + ") |\n"

# build bot comment based on response from fact check API
def buildMessage(res):
    if "claims" in res.keys() and len(res["claims"]) > 0:
        reply = replyHeader + "| Claim | Rating | Source |\n|:-|:-|:-|\n"
        for x in range(MAX_CLAIMS):
            if x == len(res["claims"]):
                break
            reply += buildTableRow(res["claims"][x])
        return reply + replyFooter
    else:
        return "I was unable to find a notable claim related to your query! Try revising your search." + replyFooter

if __name__ == "__main__":
    main()