from datetime import datetime

import googletrans
from flask import Flask, request, session as ses, render_template, redirect, abort
from sqlalchemy import create_engine, MetaData, inspect

from sqlalchemy.orm import sessionmaker, scoped_session

print()

from config.base import *
from config.local import *
from statistics import *
import requests
import json

import random
import string

def random_string(length):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choice(pool) for i in range(length))

engine = create_engine('sqlite:///'+db_path+'?check_same_thread=false', echo=True)
con = engine.connect()
session = scoped_session(sessionmaker(bind=engine))
inspector = inspect(engine)

metadata = MetaData()

print(User.__table__)
# User.__table__.create(engine)
# WordSet.__table__.create(engine)
# Word.__table__.create(engine)


session.commit()

app = Flask(__name__)
app.config['SECRET_KEY']='sdfvsdh43f3f34'

trnsh = {
    "russian":{
        "home": "главная",
        "dictionaries": "словари",
        "trainings": "тренировки",
        "settings": "настройки",
        "exit": "выход",
    }
}

trnsb = {
    "russian":{
        "Settings": "настройки",
        "Change": "Сменить",
        "disconnect VK account": "Отключить аккаунт вконтакте",
        "password": "пароль",
        "native language":"родной язык",
        "Your dictionaries":"Ваши словари",
        "Your words":"Ваши слова",
        "Select a dictionary":"Выберите словарь",
        "Imported dictionaries": "Импортированные словари",
        "Add a word here":"добавить слово в словарь",
        "word":"cлово",
        "translation":"перевод",
        "name":"название",
        "public": "публичный",
        "private": "личный",
        "add":"добавить",
        "Create a dictionary or":"Создайте новый словарь или",
        "find one":"найдите",
        "load more words":"загрузить еще",
        "spelling":"написание",
        "choose translation":"выбор перевода",
        "choose spelling": "выбор написания",
        "quick quiz":"верно/неверно"
    }
}

@app.context_processor
def load_baseInfo():
    lang = ses.get('lang',None)
    loc_head = None
    loc_body = None
    lh = lambda x:x
    lb = lambda x:x
    if not lang or (lang not in trnsh):
        loc_head = lh
    else:
        langarrh = trnsh[lang]
        def lh2(x):
            print('::-------'+x)
            if x in langarrh:
                return langarrh[x]
            return x
        loc_head = lh2
    # print(loc_head("home"))
    if not lang or (lang not in trnsb):
        loc_body = lb
        print('halt\n\n\n\n\n')
    else:
        langarrb = trnsb[lang]
        def loc(x):
            print('-------'+x)
            if x in langarrb:
                return langarrb[x]
            return x
        loc_body = loc
        print('success\n\n\n\n')
    # print(loc_body("Your dictionaries"))
    return {"loc_head":loc_head,
            "loc":loc_body}

@app.route('/')
def mp():
    if 'email' in ses:
        return redirect('/dashboard')
    return render_template('index.html')


@app.route('/jt')
def jt():
    if not ses['userId']:
        return ''

    return 'ok'



@app.route('/signin', methods=['POST'])
def sp():
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    ourUser = session.query(User).filter_by(email=email).first()
    if ourUser:
        if ourUser.password == password:
            ses['email']=email
            ses['userId']=ourUser.id
            ses['lang']=ourUser.native_language
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
    if len(name)<3 or len(email)<5 or len(password)<6:
        return redirect('/')
    if session.query(User).filter_by(email=email).first():
        return "User Already eists"
    user = User(name,email,password,native_language)
    if 'vkid' in ses:
        user.vkid=ses['vkid']
    session.add(user)
    session.commit()
    print(user)
    return 'ok'

@app.route('/search', methods=['POST'])
def searchp():
    user_id = ses['userId']
    set_name = request.json['name']
    language = request.json['language']
    res = session.query(WordSet).filter(
        WordSet.name.like('%'+set_name+'%'),
        WordSet.language==language,
        WordSet.access_type==0).all()
    print(res)
    return json.dumps([{"id":i.id,"name":i.name} for i in res])


@app.route('/trainingRes/<num>/<cors>/<incors>', methods=['GET'])
def trs(num,cors,incors):
    if 'email' in ses:
        print('---------- TRES ------------')
        cors=cors.split('_')
        incors=incors.split('_')
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
        training_id = num#request.json['trainingId']
        corrects = cors#request.json['corrects']
        incorrects = incors#request.json['incorrects']

        incWordsNum=0
        print('''
        +---------------------------------------+
        |            TRAINING RESULT            |
        +---------------------------------------+
        ''')
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




@app.route('/trainingRes/<imported>/<num>/<cors>/<incors>', methods=['GET'])
def trsi(imported,num,cors,incors):
    if 'email' in ses:
        # print('---------- TRES ------------')
        cors=cors.split('_')
        incors=incors.split('_')
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
        training_id = num#request.json['trainingId']
        corrects = cors#request.json['corrects']
        incorrects = incors#request.json['incorrects']

        incWordsNum=0
        # print('''
        # +---------------------------------------+
        # |            TRAINING RESULT            |
        # +---------------------------------------+
        # ''')
        print(user_id,training_id,corrects,incorrects)
        train_name="train"+str(training_id)
        print(train_name)
        incorrect_records = []
        correct_records = []
        if not imported == '1':
            incorrect_records = session.query(Word).filter(Word.id.in_(incorrects)).all()
            correct_records = session.query(Word).filter(Word.id.in_(corrects)).all()
        else:
            incorrect_records = session.query(ImportedWord).filter(Word.id.in_(incorrects)).all()
            correct_records = session.query(ImportedWord).filter(Word.id.in_(corrects)).all()
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
        # print(session.query(Word).filter(Word.id.in_(corrects)).all())
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
        current_date = datetime.now()
        print(current_date)
        date_str = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day)
        print(date_str)
        user = session.query(User).filter_by(id=ses['userId']).first()
        if user.last_train_date != date_str:
            year, month, day = [int(i) for i in user.last_train_date.split('-')]
            diff_days = (current_date - datetime(year=year, month=month, day=day)).days
            for i in range(diff_days):
                user.shiftStats()
            user.last_train_date = date_str
            session.commit()
        user = session.query(User).filter_by(email=ses['email']).first()
        if not user:
            return 'error'
        return render_template('dashboard.html', email=ses['email'], stats=user_statistics(session,user))
    return redirect('/')


@app.route('/dict')
def dp():
    if 'userId' in ses:
        native_language = session.query(User).filter_by(id=ses['userId']).first().native_language
        lang_code = ''
        for i in LANGUAGES:
            if i[0]==native_language:
                lang_code = i[2]
                break
        sets = session.query(WordSet).filter_by(owner_id=ses['userId']).all()
        # imported_sets = session.query(ImportedWordSet).filter_by(user_id=ses['userId']).all()
        set_pairs = session.query(ImportedWordSet, WordSet).join(WordSet, ImportedWordSet.set_id == WordSet.id) \
            .filter(ImportedWordSet.user_id == ses['userId']).all()
        imported_sets = []
        for i in set_pairs:
            imp = i[0]
            orig = i[1]
            imported_sets.append({
                "imported_id": imp.id,
                "original_name": orig.name,
                "language":orig.language
            })
        print(imported_sets)
        return render_template('dictionary.html',
                               email=ses['email'],
                               dictionaries=[i for i in sets],
                               training_names=TRAINING_NAMES,
                               nativeLanguage=native_language,
                               languages=LANGUAGES,
                               langCode=lang_code,
                               imported_sets=imported_sets,)
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
        set_pairs = session.query(ImportedWordSet, WordSet).join(WordSet, ImportedWordSet.set_id == WordSet.id) \
            .filter(ImportedWordSet.user_id == ses['userId']).all()
        imported_sets = []
        for i in set_pairs:
            imp = i[0]
            orig = i[1]
            imported_sets.append({
                "imported_id": imp.id,
                "set_name": orig.name,
                "needToTrain":8,
            })
        return render_template('choseDictForTraining.html',
                               name = name,
                               difficulty=difficulty,
                               dictionaries=[sets2[i] for i in sets2],
                               imported_dictionaries=imported_sets)
    return redirect('/')


@app.route('/startTraining/<name>/<difficulty>/<set_name>')
def training(name,difficulty,set_name):
    if 'userId' in ses:
        num = 4
        if difficulty == 'medium':
            num = 6
        elif difficulty == 'hard':
            num = 8
        if name not in TRAINING_NAMES:
            return 'wrong training name'
        if difficulty not in DIFFICULTIES:
            return "wrong difficulty"
        training_id = TRAINING_NAMES.index(name)+1
        word_set = session.query(WordSet).filter_by(owner_id=ses['userId'], name=set_name).first()
        words = session.query(Word) \
            .filter(
            Word.word_set == word_set.id,
            getattr(Word, 'train' + str(training_id)) < 3) \
            .limit(num).all()
        print(words)
        print(word_set)
        # return name+' '+difficulty
        return render_template('trainings/'+name+'.html',
                               words=words,
                               training_name=name,
                               imported=False)
    return redirect('/')

@app.route('/startTraining/<name>/<difficulty>/imported/<set_id>')
def training_imported(name,difficulty,set_id):
    if 'userId' in ses:
        if name not in TRAINING_NAMES:
            return 'wrong training name'
        if difficulty not in DIFFICULTIES:
            return "wrong difficulty"
        training_id = TRAINING_NAMES.index(name)+1
        # word_set = session.query(WordSet).filter_by(owner_id=ses['userId'], name=set_name).first()
        words = session.query(ImportedWord, Word)\
            .join(Word, ImportedWord.original_word_id == Word.id) \
            .filter(ImportedWord.import_set_id == set_id,
                    getattr(ImportedWord,'train'+str(training_id)) <3)\
            .all()
        words_to_front = map(lambda i:
                                   {'id':i[0].id,
                                    'spelling':i[1].spelling,
                                    'translation':i[1].translation}
                                   ,words)
        # session.query(ImportedWord,Word).filter(Word.word_set==word_set.id, getattr(Word,'train'+str(training_id)) <3).limit(6).all()
        print(words)
        # print(word_set)
        # return name+' '+difficulty
        return render_template('trainings/'+name+'.html',
                               words=words_to_front,
                               training_name=name,
                               imported=True)
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


@app.route('/imp_dict/<set_id>/<offset>')
def idlp(set_id,offset):
    if 'userId' not in ses:
        return redirect('/')
    # set_id = session.query(ImportedWordSet).filter_by(user_id=ses['userId'], id=dict_id).first().id
    words = [i for i in session.query(ImportedWord,Word)\
        .join(Word,ImportedWord.original_word_id==Word.id)\
        .filter(ImportedWord.import_set_id==set_id).all()]
    print(words)

    strret=''
    for i in words:
        strret += i[1].spelling+':'+str(i[0].id)+','
    if strret:
        strret=strret[:-1]
    return strret


@app.route('/train')
def trp():
    if 'userId' not in ses:
        return redirect('/')
    return render_template('trainingList.html',trainings=TRAINING_NAMES, difficulties=DIFFICULTIES)


@app.route('/addWord/<set_name>/<spelling>/<translation>', methods=['GET'])
def adw(set_name,spelling,translation):
    if 'email' in ses:
        user_id = ses['userId']
        # set_name = request.json['setName']
        set_id = session.query(WordSet).filter_by(owner_id=ses['userId'], name=set_name).first().id
        # spelling = request.json['spelling']
        # translation = request.json['translation']
        print(user_id,set_id,spelling,translation)
        if not session.query(Word).filter_by(word_set=set_id, spelling=spelling).first():
            word = Word(spelling, translation, set_id)
            session.add(word)
            session.commit()
            return 'ok'
        else:
            abort(409)
    return 'not logged in'


@app.route('/addWordSet/<name>/<language>/<privacy_type>', methods=['GET'])
def adws(language,name,privacy_type):
    if 'email' in ses:
        user_id = ses['userId']
        # language = request.json['language']
        # name = request.json['name']
        print(user_id, name, language)
        # print(dir(request))
        if not con.execute("SELECT * FROM word_sets WHERE name = '%s' and owner_id=%s"%(name,user_id)).first():
            word_set = WordSet(name, user_id, language,privacy_type)
            session.add(word_set)
            session.commit()
            return 'success'
        print(con.execute("SELECT * FROM word_sets WHERE name = '%s' and owner_id=%s"%(name,user_id)).first())
        abort(409)
    return 'not logged in'


@app.route('/getWordInfo/<word>/<word_set>', methods=['GET'])
def gwi(word,word_set):
    if 'email' in ses:
        user_id = ses['userId']
        #word = request.json['word']
        #word_set = request.json['set']
        print(user_id, word, word_set)
        word_set = session.query(WordSet).filter_by(name=word_set, owner_id=user_id).first()
        print(word_set,word_set.id)
        word_object = session.query(Word).filter_by(word_set=word_set.id, spelling=word).first()
        print(word)
        # print(dir(request))
        return word_object.translation+'; '+str(word_object.trains[:-1])[1:-1]
        abort(409)
    return 'not logged in'

@app.route('/getWordInfo/imported/<imported_word_id>/<word_set_id>', methods=['GET'])
def gwi_imported(imported_word_id,word_set_id):
    if 'email' in ses:
        user_id = ses['userId']
        #word = request.json['word']
        #word_set = request.json['set']
        print(user_id, imported_word_id, word_set_id)
        word_set = session.query(ImportedWordSet).filter_by(id=word_set_id, user_id=user_id).first()
        print(word_set,word_set.id)
        word_imp_object = session.query(ImportedWord).filter_by(import_set_id=word_set_id, id=imported_word_id).first()
        word_object = session.query(Word).filter_by(id = word_imp_object.original_word_id)
        print(imported_word_id)
        # print(dir(request))
        return word_object.translation+'; '+str(word_imp_object.trains[:-1])[1:-1]
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


@app.route('/resetStats', methods=['POST'])
def rstp():
    if 'email' in ses:
        user_id = ses['userId']
        word = request.json['word']
        word_set = request.json['set']
        word_set = session.query(WordSet).filter_by(name=word_set,owner_id=user_id).first().id
        word = session.query(Word).filter_by(word_set=word_set,spelling=word).first()
        if word:
            word.train1 = 0
            word.train2 = 0
            word.train3 = 0
            word.train4 = 0
            word.train5 = 0
            session.commit()
            return 'ok'
        return 'no such word'
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
    ses['lang']=lang
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

#@app.route('/vka',methods=['GET'])
#def vkap():
#    uid = requests.get(# 'https://oauth.vk.com/access_token?client_id=1&client_secret=H2Pk8htyFD8024mZaPHm&redirect_uri=http://mysite.ru&code='+request.get('code'))
#                 'https://oauth.vk.com/access_token?client_id=7418833&client_secret=gpRBQ3PnFXm4UPRan5S0&code='+request.args.get('code')+'&redirect_uri=http://medvosa2.pythonanywhere.com/vka').json()['user_id']
#    return 'VK user id:' + str(uid)


@app.route('/vka',methods=['GET'])
def vkap():
    ans = requests.get(# 'https://oauth.vk.com/access_token?client_id=1&client_secret=H2Pk8htyFD8024mZaPHm&redirect_uri=http://mysite.ru&code='+request.get('code'))
                 'https://oauth.vk.com/access_token?client_id=7418833&client_secret=gpRBQ3PnFXm4UPRan5S0&code='+request.args.get('code')+'&redirect_uri=http://medvosa2.pythonanywhere.com/vka').json()
    print(ans)
    uid = ans['user_id']
    user = session.query(User).filter(User.vkid==uid).all()
    if(len(user)>0):
        user = user[0]
        ses['email'] = user.email
        ses['userId'] = user.id
        return redirect('/')
    else:
        ses['vkid']=uid
        return render_template('noVk.html')

@app.route('/addvk',methods=['POST'])
def addvkp():
    if 'vkid' not in ses:
        return 'error'
    email = request.form['login']
    password = request.form['password']
    ourUser = session.query(User).filter_by(email=email).first()
    if ourUser:
        if ourUser.password == password:
            ourUser.vkid=ses['vkid']
            session.commit()
            ses['email']=email
            ses['userId']=ourUser.id
            return redirect('/dashboard')
        else:
            return 'wrong password'
    return 'No such user '+email

@app.route('/delVK')
def delvkp():
    if 'email' in ses:
        ourUser = session.query(User).filter_by(email=ses['email']).first()
        ourUser.vkid=''
        session.commit()
        return redirect('/dashboard')
    return redirect('/')

@app.route('/signupaftervk')
def savkp():
    if 'vkid' not in ses:
        return redirect('/')
    return render_template('signupvk.html')

@app.route('/dictSearch')
def dectSearch():
    return render_template('dictSearch.html', languages=LANGUAGES)

@app.route('/testpost',methods=["POST"])
def tpst():
    method = request.form.get('method')
    if not method:
        return json.dumps({"status":"error","error":"method not supplied"})
    if method=="auth":
        email = request.form.get("email")
        password = request.form.get("password")
        ourUser = session.query(User).filter_by(email=email).first()
        if not ourUser:
            return json.dumps({"status":"error","error":"authentification error"})
        if ourUser.password == password:
            key = random_string(16)#binascii.hexlify(os.urandom(16)))
            return json.dumps({"status":"ok","key":key})
        return json.dumps({"status":"error","error":"authentification error"})
    return 'ok: '+str(request.form.get('data')+str(request.form.get('userId')))


@app.route('/addPublicDict/<dict_id>')
def add_public_dictp(dict_id):
    if 'userId' not in ses:
        return redirect('/')
    word_set = session.query(WordSet).filter_by(id=dict_id).all()
    if len(word_set)==0:
        return 'error'
    word_set = word_set[0]
    if word_set.access_type==1:
       return 'access denied'
    if len(session.query(ImportedWordSet).filter_by(user_id=ses['userId'],set_id=word_set.id).all())>0:
        return 'error'
    imported = ImportedWordSet(ses['userId'],word_set.id)
    # print(imported.id)
    session.add(imported)
    print(imported.id)
    words = session.query(Word).filter_by(word_set=word_set.id).all()
    print(words)
    session.commit()
    for i in words:
        session.add(ImportedWord(imported.id,i.id))
    session.commit()
    return 'ok'


@app.route('/admin/edit/<table_name>')
def adm_edp(table_name):
    if 'admin' not in ses:
        return render_template('admin/login.html')
    print(metadata.reflect(bind=engine))
    print(metadata.tables['users'])
    columns = [i['name'] for i in inspector.get_columns(table_name)]
    return render_template('admin/edit_table.html',table_name=table_name, columns = columns, entries = [i for i in con.execute('SELECT * FROM '+table_name)])


@app.route('/admin/', methods=['GET'])
def adm_listp():
    if 'admin' not in ses:
        return render_template('admin/login.html')
    tables = con.execute('SELECT name FROM sqlite_master WHERE type =\'table\'')
    return render_template('admin/edit_tables.html', tables=[i[0] for i in tables])


@app.route('/adminl/', methods=['POST'])
def adm_loginchkp():
    login, password = request.form.get('login'),request.form.get('password')
    if login=='admin' and password==admin_password:
        ses['admin']=True
        return redirect('/admin')
    return 'error'


@app.route('/admin/save',methods=['POST'])
def adminsavep():
    if 'admin' not in ses:
        return render_template('admin/login.html')
    print(request.json)
    data = json.loads(request.form.get('data'))
    table = data['table']
    res = 'table = '+table+'\n'
    for i in data['data']:
        res+='\n'+i+' = '+str(data['data'][i])
        for j in data['data'][i]:
            con.execute('UPDATE '+table+' SET '+j+'="'+data['data'][i][j]+'" WHERE id='+str(i))
    con.commit()
    return res

@app.route('/admin/remove',methods=['POST'])
def adminremovep():
    if 'admin' not in ses:
        return render_template('admin/login.html')
    print(request.json)
    data = json.loads(request.form.get('data'))
    table = data['table']
    id = data['id']
    con.execute('DELETE FROM '+table+' WHERE id='+str(id))
    return 'ok'


@app.errorhandler(404)
def erp(n):
    return render_template("page404.html")

app.run()