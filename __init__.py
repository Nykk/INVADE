from flask import Flask, request, session as ses, render_template, redirect, abort
import random
import sys, os, signal
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine, and_
import json
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import update

from models import *

engine = create_engine('sqlite:////Volumes/High Sierra/Users/alme/PycharmProjects/INVADE/test.db?check_same_thread=false', echo=True)
con = engine.connect()
session = scoped_session(sessionmaker(bind=engine))

metadata = MetaData()

TRAINING_NAMES = ['spelling','choose translation','choose spelling','quick quiz','space invasion']
DIFFICULTIES = ['easy','medium','hard']

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

@app.route('/trainingRes/', methods=['POST'])
def trs():
    if 'email' in ses:
        user_id = ses['userId']
        training_id = request.json['trainingId']
        corrects = request.json['corrects']
        incorrects = request.json['incorrects']

        print(user_id,training_id,corrects,incorrects)
        train_name="train"+str(training_id)
        print(train_name)
        incorrect_records = session.query(Word).filter(Word.id.in_(incorrects)).all()
        correct_records = session.query(Word).filter(Word.id.in_(corrects)).all()
        print(incorrect_records)
        for i in incorrect_records:
            setattr(i,'train'+str(training_id),0)#i.train1=0
        for i in correct_records:
            setattr(i,'train'+str(training_id),getattr(i,'train'+str(training_id))+1)
        session.commit()
        print(session.query(Word).filter(Word.id.in_(corrects)).all())
        return 'ok'
    abort(409)

@app.route('/logout')
def logout():
    if 'email' in ses:
        ses.pop('email')
        ses.pop('userId')
    return redirect('/')


@app.route('/dashboard')
def db():
    if 'email' in ses:
        return render_template('dashboard.html', email=ses['email'])
    return redirect('/')


@app.route('/dict')
def dp():
    if 'userId' in ses:
        sets = session.query(WordSet).filter_by(owner_id=ses['userId']).all()
        return render_template('dictionary.html',
                               email=ses['email'],
                               dictionaries=[i.name for i in sets],
                               training_names=TRAINING_NAMES)
    return redirect('/')

@app.route('/startTraining/<name>/<difficulty>')
def stng(name,difficulty):
    if 'userId' in ses:
        sets = session.query(WordSet).filter_by(owner_id=ses['userId']).all()
        if name not in TRAINING_NAMES:
            return 'wrong training name'
        if difficulty not in DIFFICULTIES:
            return "wrong difficulty"
        # return name+' '+difficulty
        return render_template('choseDictForTraining.html',
                               name = name,
                               difficulty=difficulty,
                               dictionaries=[i.name for i in sets])
    return redirect('/')


@app.route('/startTraining/<name>/<difficulty>/<set_name>')
def training(name,difficulty,set_name):
    if 'userId' in ses:
        if name not in TRAINING_NAMES:
            return 'wrong training name'
        if difficulty not in DIFFICULTIES:
            return "wrong difficulty"
        training_id = TRAINING_NAMES.index(name)+1
        word_set = session.query(WordSet).filter_by(owner_id=ses['userId'], name=set_name).first()
        words = session.query(Word).filter(Word.word_set==word_set.id, getattr(Word,'train'+str(training_id)) <3).limit(6).all()
        print(words)
        print(word_set)
        # return name+' '+difficulty
        return render_template('trainings/'+name+'.html',words=words)
    return redirect('/')


@app.route('/dict/<name>')
def dlp(name):
    if 'userId' not in ses:
        return redirect('/')
    set_id = session.query(WordSet).filter_by(owner_id=ses['userId'], name=name).first().id
    words = session.query(Word).filter_by(word_set = set_id).all()
    print(words)
    strret=''
    for i in words:
        strret += i.spelling+','
    if strret:
        strret=strret[:-1]
    print ('returned: '+strret)
    return strret


@app.route('/train')
def trp():
    if 'userId' not in ses:
        return redirect('/')
    return render_template('trainingList.html',trainings=TRAINING_NAMES, difficulties=DIFFICULTIES)


@app.route('/addWord/', methods=['POST'])
def adw():
    if 'email' in ses:
        user_id = ses['userId']
        set_name = request.json['setName']
        set_id = session.query(WordSet).filter_by(owner_id=ses['userId'], name=set_name).first().id
        spelling = request.json['spelling']
        translation = request.json['translation']
        print(user_id,set_id,spelling,translation)
        if not session.query(Word).filter_by(word_set=set_id, spelling=spelling).first():
            word = Word(spelling, translation, set_id)
            session.add(word)
            session.commit()
            return 'ok'
        else:
            abort(409)
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
        abort(409)
    return 'not logged in'

@app.route('/getWordInfo/', methods=['POST'])
def gwi():
    if 'email' in ses:
        user_id = ses['userId']
        word = request.json['word']
        word_set = request.json['set']
        print(user_id, word, word_set)
        word_set = session.query(WordSet).filter_by(name=word_set, owner_id=user_id).first()
        print(word_set,word_set.id)
        word_object = session.query(Word).filter_by(word_set=word_set.id, spelling=word).first()
        print(word)
        # print(dir(request))
        return word_object.translation+'; '+str(word_object.trains)[1:-1]
        abort(409)
    return 'not logged in'

@app.route('/deleteWord', methods=['POST'])
def dwp():
    if 'email' in ses:
        user_id = ses['userId']
        word = request.json['word']
        word_set = request.json['set']
        word_set = session.query(WordSet).filter_by(name=word_set,owner_id=user_id).first().id
        session.query(Word).filter_by(word_set=word_set,spelling=word).delete()
        session.commit()

app.run()