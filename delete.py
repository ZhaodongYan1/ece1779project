from flask import render_template, session, request, redirect, url_for, g
from app import webapp
import mysql.connector
import random
from app.config import db_config
import os, shutil

cnx=mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

cursor = cnx.cursor()

query1 = ''' DELETE FROM credentials '''
query2 = '''ALTER TABLE credentials AUTO_INCREMENT = 1;'''
cursor.execute(query1)
cursor.execute(query2)
cnx.commit()
for item in os.listdir('app/static/'):
    if os.path.isdir('app/static/'+item):
        shutil.rmtree('app/static/'+item)

print(os.listdir('app/static/'))
#
# query1 = ''' SELECT * FROM credentials '''
# #
# cursor.execute(query1)
# for row in cursor:
#     print(row)

# for row in cursor:
#     if request.form['username']==row[0] and request.form['password']==row[1]:
#         session['authenticated'] = True
#         return redirect(url_for('upload'))