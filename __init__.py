from flask import Flask, request, session as ses, render_template, redirect
import random
import sys, os, signal
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine, and_
import json
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker

from models import *

engine = create_engine('sqlite:////Users/alme/PycharmProjects/INVADE/test.db?check_same_thread=False', echo=True)
con = engine.connect()
session = sessionmaker(bind=engine)()

metadata = MetaData()


print(User.__table__)
# User.__table__.create(engine)
# WordSet.__table__.create(engine)
# Word.__table__.create(engine)


session.commit()

app = Flask(__name__)
app.config['SECRET_KEY']='sdfvsdh43f3f34'


@app.route('/')
def mp():
    return render_template('index.html')


@app.route('/signin', methods=['POST'])
def sp():
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    ourUser = session.query(User).filter_by(email=email).first()
    if ourUser:
        if ourUser.password == password:
            ses['email']=email
            ses['userId']=ourUser.id
            return redirect('/dashboard')
        else:
            return 'wrong password'
    return 'No such user'


@app.route('/signup', methods=['POST'])
def rp():
    name = request.form.get('name', None)
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    native_language = request.form.get('language', None)
    if session.query(User).filter_by(email=email).first():
        return "User Already eists"
    user = User(name,email,password,native_language)
    session.add(user)
    session.commit()
    print(user)
    return 'ok'


@app.route('/logout')
def logout():
    if 'email' in ses:
        ses.pop('email')
        ses.pop('userId')
    return redirect('/')


@app.route('/dashboard')
def db():
    if 'email' in ses:
        return render_template('dashboard.jinja', email=ses['email'])
    return redirect('/')


@app.route('/dict')
def dp():
    if 'userId' in ses:
        sets = session.query(WordSet).filter_by(owner_id=ses['userId']).all()
        return render_template('dictionary.jinja',
            email=ses['email'],
            dictionaries=[i.name for i in sets])
    return redirect('/')


@app.route('/dict/<name>')
def dlp(name):
    if name=='english':
        return 'a,b,c,d,e,f,gh'
    return 'cat,rat,set,post,get,rest api'


@app.route('/addWord/', methods=['POST'])
def adw():
    if 'email' in ses:
        print(ses['userId'])
    return 'not logged in'


@app.route('/addWordSet/', methods=['POST'])
def adws():
    if 'email' in ses:
        user_id = ses['userId']
        language = request.json['language']
        name = request.json['name']
        print(user_id, name, language)
        # print(dir(request))
        if not con.execute("SELECT * FROM word_sets WHERE name = '%s' and owner_id=%s"%(name,user_id)).first():
            word_set = WordSet(name, user_id, language)
            session.add(word_set)
            session.commit()
            return 'success'
        return 'word st already exists'
    return 'not logged in'

app.run()