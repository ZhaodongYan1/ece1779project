from __future__ import print_function # Python 2/3 compatibility
import boto3

from boto3.dynamodb.conditions import Key

from flask import render_template, url_for, redirect, request
from app import webapp

#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")


tableName = 'SocialMediaPosts'


@webapp.route('/comprehend')
def comprehend():
    comprehend = boto3.resource('comprehend', region_name='us-east-1')
    text = request.args.get('post')
    response = comprehend.detect_sentiment(Text=text)
    return render_template("main.html",results=response)