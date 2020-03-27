from flask import Flask, request, session as ses, render_template, redirect
from flask_restful import Api, Resource, reqparse
import random
import sys, os, signal
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:////tmp/test.db', echo=True)
session = sessionmaker(bind=engine)()
Base = declarative_base()
metadata = MetaData()

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
       return "<User(id=%s, name=%s, email='%s', password='%s, native_language='%s')>" % (
                            self.id, self.name, self.email, self.password, self.native_language)

print(User.__table__)
#User.__table__.create(engine)

session.commit()

app = Flask(__name__)
app.config['SECRET_KEY']='sdfvsdh43f3f34'
api = Api(app)

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
            return 'ok'
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
    return redirect('/')

@app.route('/dashboard')
def db():
    if 'email' in ses:
        return render_template('dashboard.jinja', email=ses['email'])
    return redirect('/')

app.run()