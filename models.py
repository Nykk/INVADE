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
       return "<User(id=%s, name=%s, email='%s', password='%s, native_language='%s')>" % (
                            self.id, self.name, self.email, self.password, self.native_language)
