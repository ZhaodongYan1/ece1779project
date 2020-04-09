from __future__ import print_function # Python 2/3 compatibility
import boto3

from boto3.dynamodb.conditions import Key

from flask import render_template, url_for, redirect, request
from app import webapp

#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

tableName = 'SocialMediaPosts'




@webapp.route('/create_table')
def create_table():

    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'PostId',
                'KeyType': 'HASH'  #Partition key
            },
            {
                'AttributeName': 'Emotion',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': "CreateDateIndex",
                'KeySchema': [
                    {
                        'KeyType': 'HASH',
                        'AttributeName': 'CreateDate'
                    },
                    {
                        'KeyType': 'RANGE',
                        'AttributeName': 'PostId'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'INCLUDE',
                    'NonKeyAttributes': ['Post', 'Address']
                },
                'ProvisionedThroughput' : {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            },
            {
                'IndexName': "EmotionIndex",
                'KeySchema': [
                    {
                        'KeyType': 'HASH',
                        'AttributeName': 'Emotion'
                    },
                    {
                        'KeyType': 'RANGE',
                        'AttributeName': 'PostId'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'KEYS_ONLY'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            },
            {
                'IndexName': "AddressIndex",
                'KeySchema': [    #First key most be type HASH
                    {
                        'KeyType': 'HASH',
                        'AttributeName': 'PostAddress'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput' : {
                    'ReadCapacityUnits': 2,
                    'WriteCapacityUnits': 2
                }
            }
        ],

        AttributeDefinitions=[        #The keys you use
            {
                'AttributeName': 'PostId',
                'AttributeType': 'S'   #'S' for String
            },
            {
                'AttributeName': 'Emotion',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'CreateDate',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'PostAddress',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    return redirect(url_for('main'))


@webapp.route('/delete_table')
def delete_table():
    #dynamodb = boto3.client('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')

    response = dynamodb.delete_table(
        TableName=tableName
    )

    return redirect(url_for('main'))




def putItem(postId, emotion, title, post, createDate,
    postAddress,likes):

    table = dynamodb.Table(tableName)

    response = table.put_item(
       Item={
            'PostId': postId,
            'Emotion': emotion,
            'Title':title,
            'Post': post,
            'CreateDate': createDate,
            'PostAddress': postAddress,
            'Likes': likes
        }
    )

    return


@webapp.route('/load_data')
def load_data():

    print("Loading data into table " + tableName + "...")

    # IssueId, Title,
    # Description,
    # CreateDate, LastUpdateDate, DueDate,
    # Priority, Status

    putItem("A-101", "Negative", '0.83',
            "Being afraid in German sounds scarier than most.","2020-04-04",
            "https://www.reddit.com/r/Coronavirus/comments/futefm/in_northern_italy_60_volunteers_who_thought_theyd/",
            "242")

    putItem("A-102", "Positive",'0.99',
            "It's fun sounding these out and dissecting roots","2020-04-04",
            "https://www.reddit.com/r/Coronavirus/comments/futefm/in_northern_italy_60_volunteers_who_thought_theyd/",
            "29")

    putItem("A-103", "Neutral",'0.96',
            "Gentle reminder that Jeff Epstein didn’t kill himself.","2020-04-04",
            "https://www.reddit.com/r/worldnews/comments/furx8f/sell_one_of_your_three_yachts_outrage_as/",
            "107")

    putItem("A-104", "Negative",'0.87',
            "Just a shame that Trump doesn't give a shit about Detroit.","2020-04-04",
            "https://www.reddit.com/r/worldnews/comments/fu95vz/trump_orders_medical_supply_firm_3m_to_stop/",
            "533")

    putItem("A-105", "Negative",'0.89',
            "It's pretty sad that a first world country has to do something like this to a small country like mine","2020-04-04",
            "https://www.reddit.com/r/worldnews/comments/fua4yw/coronavirus_face_masks_bound_for_canada_and/",
            "4.5k")


    return redirect(url_for('main'))


@webapp.route('/list_all/<indexName>')
def list_all(indexName):

    table = dynamodb.Table(tableName)

    response = table.scan(IndexName = indexName)

    records = []

    for i in response['Items']:
        records.append(i)

    while 'LastEvaluatedKey' in response:
        response = table.scan(
            IndexName=indexName,
            ExclusiveStartKey=response['LastEvaluatedKey']
            )

        for i in response['Items']:
            records.append(i)

    return render_template("issues.html", issues=records)


@webapp.route('/query_createdate')
def query_createdate():
    table = dynamodb.Table(tableName)

    date = request.args.get('date')

    response = table.query(
        IndexName = 'CreateDateIndex',
        KeyConditionExpression= Key('CreateDate').eq(date) & Key('PostId').begins_with("A-")
    )

    records = []

    for i in response['Items']:
        records.append(i)

    return render_template("issues.html", issues=records)


@webapp.route('/query_emotion')
def query_emotion():
    table = dynamodb.Table(tableName)

    emotion = request.args.get('emotion')

    response = table.query(
        IndexName = 'EmotionIndex',
        KeyConditionExpression= Key('Emotion').eq(emotion)
    )

    records = []

    for i in response['Items']:
        records.append(i)

    return render_template("issues.html", issues=records)


@webapp.route('/query_address')
def query_address():
    table = dynamodb.Table(tableName)

    postaddress = request.args.get('postaddress')

    response = table.query(
        IndexName = 'AddressIndex',
        KeyConditionExpression= Key('PostAddress').eq(postaddress)
    )

    records = []

    for i in response['Items']:
        records.append(i)

    return render_template("issues.html", issues=records)

@webapp.route('/dynamo')
def dynamo():
    return render_template("dynamo.html")

