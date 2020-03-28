from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine

Base = declarative_base()

class User(Base):
    __tablename__='users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    native_language = Column(String)
    
    def __init__(self, name, email, password, native_language):
        self.name = name
        self.email = email
        self.password = password
        self.native_language=native_language

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
    word_set = Column(String)
    train1 = Column(Integer)
    train2 = Column(Integer)
    train3 = Column(Integer)
    train4 = Column(Integer)
    train5 = Column(Integer)

    def __init__(self, spelling, translation, word_set):
        self.spelling = spelling
        self.translation = translation
        self.word_set = set
        self.train1 = 0
        self.train2 = 0
        self.train3 = 0
        self.train4 = 0
        self.train5 = 0

    def __repr__(self):
        return "<Word(id=%s, spelling=%s, translation='%s', set='%s, trains='%s')>" % (
            self.id, self.spelling, self.translation, self.set,
            [self.train1,self.train2,self.train3,self.train4,self.train5])
