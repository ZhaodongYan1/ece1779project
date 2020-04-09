from __future__ import print_function # Python 2/3 compatibility
import boto3

from boto3.dynamodb.conditions import Key

from flask import render_template, url_for, redirect, request, session
from app import webapp
from app.dynamo import putItem
#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")


def getSentiment(text):
    comprehend = boto3.client('comprehend')
    text = request.form.get('text')
    response = comprehend.detect_sentiment(Text=text,LanguageCode='en')
    sentiment = response['Sentiment']
    result = sentiment + '; ' + str(response['SentimentScore'])
    return result

def detectLanguage(text):
    comprehend = boto3.client('comprehend')
    response = comprehend.detect_dominant_language(
        Text=text
    )
    return response['Languages'][0]['LanguageCode']

def translate(text,targetLang='en'):
    client = boto3.client('translate')
    response = client.translate_text(
    Text=text,
    SourceLanguageCode='auto',
    TargetLanguageCode=targetLang)
    return response['TranslatedText']



@webapp.route('/loadreddit',methods=['POST','GET'])
def load_reddit():
    import praw
    from datetime import datetime
    comprehend = boto3.client('comprehend')
    reddit = praw.Reddit(client_id='VcSCegzGWO8Frg',
                         client_secret='1IVb5rrY7YbfDJVhkq2jRWabvCU',
                         user_agent='prawuseragent',
                         username='ece1779agent',
                         password='Yan8318161')

    for submission in reddit.subreddit('popular').hot(limit=1):
        title = str(submission.title)
        url = str(submission.url)
        submission.comments.replace_more(limit=0)
        for top_level_comment in submission.comments:
            comment = top_level_comment.body
            str_comment = comment
            if len(str_comment) > 5000:
                str_comment = str_comment[:5000]
            score = str(top_level_comment.score)
            time = str(datetime.fromtimestamp(top_level_comment.created))
            if str_comment != None:
                response = comprehend.detect_sentiment(Text=str_comment,LanguageCode='en')
                sentiment = str(response['SentimentScore'])
                putItem("A-1098", sentiment, title,
                        str_comment, time,
                        url,
                        score)
                break

    return render_template("user_interface.html")



@webapp.route('/comprehend',methods=['POST','GET'])
def comprehend():

    text = request.form.get('text')
    targetLang = request.form.get('target_lan')
    translatedText = translate(text,targetLang=targetLang)

    sentiment = getSentiment(text)
    from gingerit.gingerit import GingerIt
    grammar=GingerIt().parse(text)['result']
    return render_template("user_interface.html",user=session['username'], Text=text, sentiment=sentiment,translatedText=translatedText,text=text,grammar=grammar)

@webapp.route('/textextract',methods=['POST','GET'])
def textextract():

    return render_template("fileupload/form.html")

