from __future__ import print_function # Python 2/3 compatibility
import boto3

from boto3.dynamodb.conditions import Key

from flask import render_template, url_for, redirect, request, session, Markup
from app import webapp
from app.dynamo import putItem
from app.gingerit_custom import GingerIt

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
    import re
    text = request.form.get('text')
    targetLang = request.form.get('target_lan')
    translatedText = translate(text,targetLang=targetLang)

    sentiment = getSentiment(text)
    if len(text)>590:
        print(text)
        tmp=0
        color_result_=''
        color_text_=''
        regex = re.compile("[,.!?:]")
        text = re.sub('([.,!?:])', r'\1 ', text)
        text = re.sub('\s{2,}', ' ', text)
        words=text.split()
        for i, item in enumerate(words):
            if regex.search(item)!=None:
                results=GingerIt().parse(' '.join(words[tmp:i+1]))
                color_result_ +=results['color_r']
                color_text_ +=results['color_t']
                tmp=i+1
        if tmp!=len(words)+1:
            results = GingerIt().parse(' '.join(words[tmp:]))
            color_result_ += results['color_r']
            color_text_ += results['color_t']

        color_result=Markup(color_result_)
        color_text=Markup(color_text_)

    else:
        results=GingerIt().parse(text)
        color_result=Markup(results['color_r'])
        color_text=Markup(results['color_t'])
    return render_template("user_interface.html",user=session['username'], Text=text, sentiment=sentiment,translatedText=translatedText,text=text,corrected=color_result, original=color_text)

@webapp.route('/textextract',methods=['POST','GET'])
def textextract():

    return render_template("fileupload/form.html")

