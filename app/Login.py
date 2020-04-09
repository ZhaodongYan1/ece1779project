from flask import render_template, session, request, redirect, url_for, g
from app import webapp
import random
import datetime
import os, hashlib, uuid
import re, json
import boto3
from boto3.dynamodb.conditions import Key, Attr

webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'


@webapp.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    return redirect(url_for('login_v2'))


@webapp.route('/login_v2',methods=['GET','POST'])
def login_v2():
    uname = None
    e = None
    if 'authenticated' in session:
        return redirect(url_for('user_interface'))

    if 'username' in session: 
        uname = session['username']
        session.pop('username', None)
    if 'error' in session:
        e = session['error']
        session.pop('error', None)
    return render_template("login.html", error=e, username=uname)


# url_for('static', filename='coke.jpg')
@webapp.route('/login_submit_v2',methods=['POST'])
def login_submit_v2():
    client = boto3.resource('dynamodb')
    table = client.Table("1779user")
    username = request.form.get('username', "")
    password = request.form.get('password', "")

    item = table.query(KeyConditionExpression=Key('username').eq(username))

    if username == "" or password == "":
        session['error'] = "Error: All fields are required!"
        return redirect(url_for('login_v2'))

    if len(username) > 100 or len(password) > 100:
        session['error'] = "Error: username or password exceeds maximum length"
        return redirect(url_for('login_v2'))

    if item['Items'] == []:
        return {
            'statusCode': 400,
            'body': "login failed"
        }
    # valid login by comparing salt and hash from database
    salt = item['Items'][0]['salt']
    hash = item['Items'][0]['hash']

    salted_password = "{}{}".format(salt, password)
    m = hashlib.md5()
    m.update(salted_password.encode('utf-8'))
    new_hash = m.digest()

    if str(hash) == str(new_hash):
        session['authenticated'] = True
        session['username'] = username
        session['userid'] = username ###
        session.permanent = True
        webapp.permanent_session_lifetime = datetime.timedelta(hours=24)
        return redirect(url_for('user_interface'))
    else:
        if 'username' in request.form:
            session['username'] = username
        session['error'] = "Error! Incorrect username or password!"
        return redirect(url_for('login_v2'))


@webapp.route('/user/create',methods=['GET'])
def user_create():
    return render_template("login.html", title="New User")


@webapp.route('/user/create', methods=['POST'])
def user_create_save():
    username = request.form.get('username', "")
    password = request.form.get('password', "")

    error = False
    if username == "" or password == "":
        error = True
        error_msg = "Error: All fields are required!"
    elif re.match('^(?=.{3,100}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$', username) == None:
        # Username is 8-20 long, no _ or . at the beninning,  no __ or _. or ._ or .. inside,no _ or . at the end
        error = True
        error_msg = "Error: username is invalid"
    elif len(password) < 3 or len(password) > 30:
        error = True
        error_msg = "Error: password is invalid"
    else:

        client = boto3.resource('dynamodb')
        table = client.Table("1779user")
        print(Key('username'),111)
        item = table.query(KeyConditionExpression=Key('username').eq(username))
        if item['Items'] != []:
            error = True
            error_msg = "Error: user existed"
        else:
            # save password as hash and salt
            salt = str(random.getrandbits(16))
            salted_password = "{}{}".format(salt, password)
            m = hashlib.md5()
            m.update(salted_password.encode('utf-8'))
            hash = m.digest()
            response = {'username': username, 'hash': str(hash), 'salt': str(salt)}
            table.put_item(Item=response)

    if error:
        return render_template("login.html", title="New User", error=error_msg, username=username,  password=password)\

    session['error']='Registration complete. Please sign in'
    session['username'] = username
    return redirect(url_for('login_v2'))


@webapp.route('/user_interface', methods=['GET', 'POST'])
def user_interface():
    if 'authenticated' not in session:
        return redirect(url_for('login_v2'))
    return render_template("user_interface.html", user=session['username'])


