from flask import render_template, redirect, session, url_for, request, g
from app import webapp
from datetime import datetime
import os, hashlib, uuid, re

import json

import random
from boto3.dynamodb.conditions import Key
import boto3
import urllib.request
from io import BytesIO

webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'


@webapp.route('/test/FileUpload/form',methods=['GET'])
#Return file upload form
def upload_form():
    e=None
    if 'error2' in session:
        e=session['error2']
        session.pop('error2', None)
    return render_template("fileupload/form.html", error=e)


@webapp.route('/test/FileUpload',methods=['POST'])
#Upload a new file and store in the systems temp directory
def file_upload():

    UserID = session.get('username')

    # check if the post request has the file part
    if 'uploadedfile' not in request.files:
        session['error2']= "Error: Missing uploaded file"
        return redirect(url_for('upload_form'), url_=None)

    new_file = request.files['uploadedfile']

    # if user does not select file, browser also
    # submit a empty part without filename
    if new_file.filename == '':
        session['error2'] = "Error: Missing uploaded file"
        return redirect(url_for('upload_form'), url_=None)

    filename_full = new_file.filename
    index = filename_full.rfind('.')
    filename = filename_full[:index]+str(datetime.timestamp(datetime.now())).replace('.','')
    # filename=new_file.filename.replace('.', str(datetime.timestamp(datetime.now())).replace('.','')+'.')
    new_file.seek(0, os.SEEK_END)
    size = new_file.tell()
    if size>1E8:

        session['error2'] = "Error: Selected Image too large(>100MB)"
        return redirect(url_for('upload_form'), url_=None)

    # Get the service client and upload to the s3 bucket
    new_file.seek(0)
    s3 = boto3.client('s3')
    username = session['username']
    s3.upload_fileobj(new_file, 'ece1779project', username+'/textract/'+filename, ExtraArgs={"ContentType": "image/jpeg"})

    # from PIL import Image
    # testfile = Image.frombytes("RGB",(128,128),new_file)
    # get the url of the upload image
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'ece1779project', 'Key': username+'/textract/'+filename})

    textract = boto3.client('textract')
    response = textract.detect_document_text(
        Document={
            'S3Object':{
                'Bucket':'ece1779project',
                'Name':username+'/textract/'+filename
            }
        }
    )
    text = []
    result = response['Blocks']
    for e in result:
        try:
            if e['BlockType']=='WORD':
                text.append(e['Text'])
        except:
            pass
    text = ' '.join(text)
    # yolo_process(os.path.join(tempdir,filename))
    session['error2'] = "Upload Successful"
    e = None
    if 'error2' in session:
        e = session['error2']
        session.pop('error2', None)
    return render_template("fileupload/form.html", error=e, text=text, url_=url)

@webapp.route('/api/upload',methods=['GET'])
#Return file upload form
def form_api():
    return render_template("fileupload/form_api.html")




