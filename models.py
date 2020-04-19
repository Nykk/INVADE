from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__='users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    native_language = Column(String)
    words_learned_by_days = Column(String)
    trains_completed_by_days = Column(String)
    last_train_date = Column(String)

    def __init__(self, name, email, password, native_language):
        self.name = name
        self.email = email
        self.password = password
        self.native_language = native_language
        self.words_learned_by_days = '0,0,0,0,0,0,0'
        self.trains_completed_by_days = '0,0,0,0,0,0,0'
        self.last_train_date = '2020-02-10'

    def incWordsToday(self, num):
        wordsList = self.words_learned_by_days.split(',')
        wordsList[0]=str(int(wordsList[0])+num)
        self.words_learned_by_days = ','.join(wordsList)

    def incTrainingsToday(self, num):
        trainsList = self.trains_completed_by_days.split(',')
        trainsList[0] = str(int(trainsList[0])+num)
        self.trains_completed_by_days = ','.join(trainsList)

    def shiftStats(self):
        wordsList = self.words_learned_by_days.split(',')
        wordsList.pop()
        wordsList=['0']+wordsList

        trainsList = self.trains_completed_by_days.split(',')
        trainsList.pop()
        trainsList=['0']+trainsList

        self.words_learned_by_days = ','.join(wordsList)
        self.trains_completed_by_days = ','.join(trainsList)

    def __repr__(self):
       return "<User(id=%s, name=%s, email='%s', password='%s', native_language='%s')>" % (
                            self.id, self.name, self.email, self.password, self.native_language)


class WordSet(Base):
    __tablename__ = 'word_sets'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner_id = Column(Integer)
    language = Column(String)

    def __init__(self, name, owner_id, language):
        self.name = name
        self.owner_id = owner_id
        self.language = language
        # self.native_language = native_language

    def __repr__(self):
        return "<WordSet(id=%s, name=%s, owner_id='%s', language='%s')>" % (
            self.id, self.name, self.owner_id, self.language)


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    spelling = Column(String)
    translation = Column(String)
    word_set = Column(Integer)
    train1 = Column(Integer)
    train2 = Column(Integer)
    train3 = Column(Integer)
    train4 = Column(Integer)
    train5 = Column(Integer)

    def __init__(self, spelling, translation, word_set):
        self.spelling = spelling
        self.translation = translation
        self.word_set = word_set
        self.train1 = 0
        self.train2 = 0
        self.train3 = 0
        self.train4 = 0
        self.train5 = 0

    @property
    def trains(self):
        return [self.train1,self.train2,self.train3,self.train4,self.train5]

    def __repr__(self):
        return "<Word(id=%s, spelling=%s, translation='%s', set=%s, trains='%s')>" % (
            self.id, self.spelling, self.translation, self.word_set,
            [self.train1,self.train2,self.train3,self.train4,self.train5])
