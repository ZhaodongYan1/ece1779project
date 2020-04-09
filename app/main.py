
from flask import render_template, url_for, redirect
from app import webapp

import datetime


@webapp.route('/')
def main():
    return redirect(url_for('login_v2'))



