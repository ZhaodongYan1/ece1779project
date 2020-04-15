from __future__ import print_function # Python 2/3 compatibility
import boto3

from boto3.dynamodb.conditions import Key

from flask import render_template, url_for, redirect, request, session, Markup
from app import webapp
from app.dynamo import putItem
from app.gingerit_custom import GingerIt
import re
#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
from datetime import datetime

def getSentiment(text):
    comprehend = boto3.client('comprehend')
    text = request.form.get('text')
    response = comprehend.detect_sentiment(Text=text,LanguageCode='en')
    sentiment = response['Sentiment']
    details = ''
    for k,v in response['SentimentScore'].items():
        details += str(k) + ': ' +str(v)+'\n'
    result = 'Sentiment: ' + sentiment + '\nDetails: \n' + details
    return result

def detectLanguage(text):
    comprehend = boto3.client('comprehend')
    response = comprehend.detect_dominant_language(
        Text=text
    )
    return response['Languages'][0]['LanguageCode']

def translate_(text,targetLang='en'):
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

@webapp.route('/textract',methods=['POST','GET'])
def textract():
    return render_template("fileupload/form.html", url_=None)
@webapp.route('/translate',methods=['POST','GET'])
def translate():
    return render_template("translate.html")
@webapp.route('/sentiment',methods=['POST','GET'])
def sentiment():
    return render_template("sentiment.html")
@webapp.route('/grammarcheck',methods=['POST','GET'])
def grammarcheck():
    return render_template("grammarcheck.html")

@webapp.route('/sentiment_submit',methods=['POST','GET'])
def sentiment_submit():
    text = request.form.get('text')
    sentiment = getSentiment(text)
    body='Text: '+text+'\nSentiment: '+sentiment
    filename=str(datetime.timestamp(datetime.now())).replace('.','')
    username=session['username']
    client = boto3.client('s3')
    client.put_object(Body=body, Bucket='ece1779project', Key= username+'/sentiment/'+filename+'.txt')
    return render_template("sentiment.html", Text=text,sentiment=sentiment)
@webapp.route('/translate_submit',methods=['POST','GET'])
def translate_submit():
    text = request.form.get('text')
    targetLang = request.form.get('target_lan')
    translatedText = translate_(text,targetLang=targetLang)
    filename=str(datetime.timestamp(datetime.now())).replace('.','')
    body='Text: '+text+'\nTranslation: '+translatedText
    username=session['username']
    client = boto3.client('s3')
    client.put_object(Body=body, Bucket='ece1779project', Key= username+'/translation/'+filename+'.txt')
    return render_template("translate.html", Text=text,Translation=translatedText)
@webapp.route('/grammar_submit', methods=['POST', 'GET'])
def grammar_submit():
    text = request.form.get('text')
    if len(text)>590:
        print(text)
        tmp=0
        color_result_=''
        color_text_=''
        result=''
        regex = re.compile("[,.!?:]")
        text = re.sub('([.,!?:])', r'\1 ', text)
        text = re.sub('\s{2,}', ' ', text)
        words=text.split()
        for i, item in enumerate(words):
            if regex.search(item)!=None:
                results=GingerIt().parse(' '.join(words[tmp:i+1]))
                color_result_ +=results['color_r']
                color_text_ +=results['color_t']
                result+=results['result']
                tmp=i+1
        if tmp!=len(words)+1:
            results = GingerIt().parse(' '.join(words[tmp:]))
            color_result_ += results['color_r']
            color_text_ += results['color_t']
            result += results['result']

        color_result=Markup(color_result_)
        color_text=Markup(color_text_)
    else:
        results=GingerIt().parse(text)
        result = results['result']
        color_result=Markup(results['color_r'])
        color_text=Markup(results['color_t'])
    filename=str(datetime.timestamp(datetime.now())).replace('.','')
    body='Text: '+text+'\nCorrection: '+result
    username=session['username']
    client = boto3.client('s3')
    client.put_object(Body=body, Bucket='ece1779project', Key= username+'/grammar/'+filename+'.txt')
    return render_template("grammarcheck.html",user=session['username'], Text=text, corrected=color_result, original=color_text)