from sqlalchemy import *
from sqlalchemy.sql import *
import os, hashlib


# Pour le hash du password
#app.secret_key = 'iswuygdedgv{&75619892__01;;>..zzqwQIHQIWS'
SALT = 'foo#BAR_{baz}^666'

def hash_for(password):
	salted = '%s @ %s' % (SALT, password)
	return hashlib.sha256(salted.encode('utf-8')).hexdigest()

# Création de la base de données
# Base de donnée : doit supporter les types "blob"
engine = create_engine('sqlite:///lama.db', echo=True)
metadata = MetaData()

user = Table('user', metadata,
	Column('username', String, primary_key = True, unique = True, nullable = False),
	Column('password', String),
	Column('mail', String),
	Column('lastname', String),
	Column('name', String),
	Column('address', String),
	Column('profile_image_path', String),
	Column('creation_date', String),
	Column('score', Integer),
	Column('birthdate', String),
	Column('telephone', String))

project = Table('project', metadata,
	Column('id', Integer, autoincrement = True, primary_key = True, nullable = False, unique = True),
	Column('creation_date', String),
	Column('user', String, ForeignKey('user.username', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('project_name', String),
	Column('dimensionsx', Integer),
	Column('dimensionsy', Integer),
	Column('dimensionsz', Integer),
	Column('image_path', String),
	Column('price', Integer),
	Column('score', Integer),
	Column('project_type', Integer), #'rquest', 'publication' ou 'offer'
	Column('description', String))

file = Table('file', metadata,
	Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
	Column('creation_date', String),
	Column('score', Integer),
	Column('project', Integer, ForeignKey('project.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('file_path', String),
	Column('dimensionsx', Integer),
	Column('dimensionsy', Integer),
	Column('dimensionsz', Integer),
	Column('city', String),
	Column('weight', Float),
	Column('price', Integer),
	Column('name', String))
	
	
printer = Table('printer', metadata,
	Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
	Column('creation_date', String),
	Column('user', String, ForeignKey('user.username', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('dimensionsx', Integer),
	Column('dimensionsy', Integer),
	Column('dimensionsz', Integer),
	Column('resolution', String),
	Column('postal_code', Integer),
	Column('country', String),
	Column('weight', Float),
	Column('price', String)) # exemple: '€23.4'

				
comment = Table('comment', metadata,
	Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
	Column('creation_date', String),
	Column('score', Integer),
	Column('project', Integer, ForeignKey('project.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('user', String, ForeignKey('user.username', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('comment_text', String))


metadata.create_all(engine)		# remplit la BdD avec les informations par défaut

db = engine.connect()

#db.execute(user.insert(), [
#	{'username':'the dark knight', 'password':hash_for('123'), 'mail':'batman@dc.com', 'lastname':'Wayne', 'name':'Bruce', 'address':'the batcave', 'creation_date':'01011990', 'score': 0, 'printer':'yes', 'telephone':'1234'},
#	{'username':'matias', 'password':hash_for('123'), 'mail':'matias@gmail.com', 'lastname':'Dwek', 'name':'Matias', 'address':'TC', 'creation_date':'01011990', 'score': 0, 'printer':'no', 'telephone':'1234'},
#	{'username':'lama', 'password':hash_for('123'), 'mail':'lama@lama.lama', 'lastname':'lama', 'name':'lama', 'address':'lama', 'creation_date':'01011990', 'score': 0, 'printer':'yes', 'telephone':'1234'},
#	{'username':'lama1', 'password':hash_for('123'), 'mail':'lama@lama.lama', 'lastname':'lama', 'name':'lama', 'address':'lama', 'creation_date':'01011990', 'score': 0, 'printer':'yes', 'telephone':'1234'}
#])

db.execute(printer.insert(), [
	{},
])

db.execute(printer.insert(), [
	{'dimensionsx':5, 'description':'good printer'},
	{'dimensionsx':6, 'description':'bad printer'}
])

stmt = "select * from printer where dimensionsx <= \"6\""
#stmt = "select * from printer"

for row in db.execute(stmt):
    print(row)
print('\n')


db.close()

