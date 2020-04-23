from datetime import datetime

import googletrans
from flask import Flask, request, session as ses, render_template, redirect, abort
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session

print()

from config.base import *
from config.local import db_path
from statistics import *

engine = create_engine('sqlite:///'+db_path+'?check_same_thread=false', echo=True)
con = engine.connect()
session = scoped_session(sessionmaker(bind=engine))

metadata = MetaData()

print(User.__table__)
# User.__table__.create(engine)
# WordSet.__table__.create(engine)
# Word.__table__.create(engine)


session.commit()

app = Flask(__name__)
app.config['SECRET_KEY']='sdfvsdh43f3f34'

@app.context_processor
def load_baseInfo():
    return {"totalWords":43}

@app.route('/')
def mp():
    if 'email' in ses:
        return redirect('/dashboard')
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


@app.route('/inc')
def iws():
    if 'userId' not in ses:
        return ''
    user = session.query(User).filter_by(id=ses['userId']).first()
    if user:
        user.incWordsToday(1)
        session.commit()
    else:
        return 'Internal server error'
    return 'ok'


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
        current_date = datetime.now()
        print(current_date)
        date_str = str(current_date.year)+'-'+str(current_date.month)+'-'+str(current_date.day)
        print(date_str)
        user = session.query(User).filter_by(id=ses['userId']).first()
        if user.last_train_date!=date_str:
            year,month,day = [ int(i) for i in user.last_train_date.split('-')]
            diff_days = (current_date - datetime(year=year, month=month,day=day)).days
            user.last_train_date = date_str
            for i in range(diff_days):
                user.shiftStats()
        user_id = ses['userId']
        training_id = request.json['trainingId']
        corrects = request.json['corrects']
        incorrects = request.json['incorrects']

        incWordsNum=0

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
            if i.train1==i.train2==i.train3==i.train4==3:
                print(i)
                incWordsNum+=1
        if incWordsNum>0:
            user.incWordsToday(incWordsNum)
        user.incTrainingsToday(1)
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
        user = session.query(User).filter_by(email=ses['email']).first()
        if not user:
            return 'error'
        return render_template('dashboard.html', email=ses['email'], stats=user_statistics(session,user))
    return redirect('/')


@app.route('/dict')
def dp():
    if 'userId' in ses:
        native_language = session.query(User).filter_by(id=ses['userId']).first().native_language
        sets = session.query(WordSet).filter_by(owner_id=ses['userId']).all()
        return render_template('dictionary.html',
                               email=ses['email'],
                               dictionaries=[i for i in sets],
                               training_names=TRAINING_NAMES,
                               nativeLanguage=native_language)
    return redirect('/')

@app.route('/startTraining/<name>/<difficulty>')
def stng(name,difficulty):
    if 'userId' in ses:

        if name not in TRAINING_NAMES:
            return 'wrong training name'
        if difficulty not in DIFFICULTIES:
            return "wrong difficulty"
        training_id = TRAINING_NAMES.index(name) + 1
        sets = session.query(WordSet).filter_by(owner_id=ses['userId']).all()
        sets2={}
        for i in sets:
            # print(i.id)
            # print(session.query(Word).filter_by(word_set=i.id).count())
            sets2[i.id]={"setName":i.name,
                         "wordCount":session.query(Word).filter_by(word_set=i.id).count(),
                         "needToTrain":session.query(Word).filter(Word.word_set==i.id,getattr(Word,'train'+str(training_id)) <3).count()}
        for i in sets2:
            print(i,sets2[i])
        # return name+' '+difficulty
        return render_template('choseDictForTraining.html',
                               name = name,
                               difficulty=difficulty,
                               dictionaries=[sets2[i] for i in sets2])
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
        return render_template('trainings/'+name+'.html',words=words, training_name=name)
    return redirect('/')


@app.route('/dict/<name>/<offset>')
def dlp(name,offset):
    if 'userId' not in ses:
        return redirect('/')
    set_id = session.query(WordSet).filter_by(owner_id=ses['userId'], name=name).first().id
    words = session.query(Word).filter_by(word_set = set_id).limit(9).offset(offset).all()
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
        return word_object.translation+'; '+str(word_object.trains[:-1])[1:-1]
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
        return 'ok'
    return 'not logged in'

@app.route('/settings')
def stp():
    if 'email' not in ses:
        return redirect('/')
    user = session.query(User).filter_by(email=ses['email']).first()
    if not user:
        abort(401)
    return render_template("settings.html", languages=LANGUAGES, current_language=user.native_language)


@app.route('/settings/setlang/<lang>')
def stlp(lang):
    if 'email' not in ses:
        return redirect('/')
    user = session.query(User).filter_by(email=ses['email']).first()
    if not user:
        abort(401)
    user.native_language=lang
    session.commit()
    return 'ok'


@app.route('/settings/setpassword', methods=['POST'])
def spp():
    if 'email' not in ses:
        return redirect('/')
    password = request.json['password']
    password_repeat = request.json['passwordRepeat']
    user = session.query(User).filter_by(email=ses['email']).first()
    if not user:
        abort(401)
    if password==password_repeat and len(password)>=6:
        user.password = password
        session.commit()
        return 'ok'
    return 'error'

@app.route('/getinfo/<wd>/<to>')
def trpg(wd,to):
    rs=[]
    def parse_out(out):
        for i in out:
            for j in i[1]:
                rs.append(j)
    print('aaa')
    parse_out(googletrans.Translator().translate(wd,to).extra_data['all-translations'])
    # print(parse_out(googletrans.Translator().translate(wd,to).extra_data['all-translations']))
    ret = '{"word":"'+wd+'","translation":['
    for i in rs:
        ret+='"'+ i +'",'
    ret=ret[:-1]
    ret+=']}'
    return ret



@app.errorhandler(404)
def erp(n):
    return render_template("page404.html")

app.run()