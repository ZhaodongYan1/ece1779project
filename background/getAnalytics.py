import json, boto3


# connect to API Gateway to display user usage
def lambda_handler(event, context):
    username = event['username']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('a3Analytics')
    response = table.get_item(Key={'requestID': username})

    response = response['Item']
    #  return response['Item']
    return '<!DOCTYPE html><html><head><style>table, th, td {border: 1px solid black;border-collapse: collapse;}'+'th, td {padding: 15px;text-align:left;}</style></head><body><h2>Usage statistics</h2>'+'<table style="width:100%">  <tr>    <th>Username</th><th>Textract Requests</th> <th>Textract file size</th><th>'+'Sentiment Requests</th><th>Sentiment file size</th><th>Translation Requests</th><th>Translation file size</th><th>Grammar Requests</th> '+'<th>Grammar file size</th></tr><tr><td>'+str(username)+'</td><td>'+str(response['textract_req'])+'</td><td>'+str(response['textract_size'])+'</td><td>'+str(response['sentiment_req'])+'</td><td>'+str(response['sentiment_size'])+'</td><td>'+str(response['translation_req'])+'</td><td>'+str(response['translation_size'])+'</td><td>'+str(response['grammar_req'])+'</td><td>'+str(response['grammar_size'])+'</td></table><br></body></html>'


