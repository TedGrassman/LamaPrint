#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import *
from sqlalchemy import *
from sqlalchemy.sql import *
from markdown import markdown
import os, hashlib


app = Flask(__name__)

# Pour le hash du password
#app.secret_key = 'iswuygdedgv{&75619892__01;;>..zzqwQIHQIWS'
app.secret_key = os.urandom(256)
SALT = 'foo#BAR_{baz}^666'

# Création de la base de données
# Base de donnée : doit supporter les types "blob"
engine = create_engine('sqlite:///users.db', echo=True)
metadata = MetaData()

accounts = Table('accounts', metadata,
	Column('id', Integer, autoincrement=True, primary_key=True),
	Column('login', String, nullable=False),
	Column('password_hash', String, nullable=False))

metadata.create_all(engine)		# remplit la BdD avec les informations par défaut


def hash_for(password):
	salted = '%s @ %s' % (SALT, password)
	return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def authenticate(login, password):
	"""Authentifier un utilisateur"""
	db = engine.connect()
	try:
		name = db.execute(select([accounts.c.login]).where(accounts.c.login == login)).fetchone()
		print('User', name)
		if name is None:
			# L'utilisateur n'existe pas
			# code ...
			print('**Authentication fail: login does not exist**')
			return False
		else:
			passhash = hash_for(password)
			#passhash = hash_for(password.encode('utf-8'))
			#storedHash = db.execute(select([accounts.c.password_hash]).where(accounts.c.login == login)).fetchone()
			print(login)
			print(password)
			result = db.execute("select password_hash from accounts where login=\'"+login+"\'")
			"""for i in result:
				print(i)
				storedHash = i"""
			storedHash = result.fetchone()[0]
			print(passhash)
			print(storedHash)
			if passhash == storedHash:
				print('**Authentication successfull!**')
				return True
			else:
				print('**Authentication fail: wrong password**')
				return False
	finally:
		db.close();

def create(login, password):
	"""Créer et enregistrer un utilisateur existant"""
	db = engine.connect()
	try:
		name = db.execute(select([accounts.c.login]).where(accounts.c.login == login)).fetchone()
		print(name)
		if name is None:
			# L'utilisateur n'existe pas ; on l'ajoute
			db.execute(accounts.insert(), [ {'login': login, 'password_hash': hash_for(password)} ])
			print('**(New user)**')
			return True
		else:
			# L'utilisateur existe déjà ; erreur
			print('**Creation fail: login already exists**')
			return False
	finally:
		db.close();
				

@app.route('/')
@app.route('/index')
def index():
	return redirect(url_for('static', filename='index.html'))

@app.route('/test')
def test():
	return "Hello !"

@app.route('/login', methods=['GET', 'POST'])
def login():
	from_page = request.args.get('from', 'Main')
	if request.method == 'POST':
		if authenticate(request.form['login'], request.form['password']):	# le login a réussi (True)
			session['username'] = request.form['login']
			#session['name'] = escape(request.form['name'])              
			session['logged'] = True
			flash('Authentication successfull')
			print('Authentication successfull')
			return redirect('/')		# on redirige à l'index
		else:		# authenticate a échoué (False)
			flash('Unexistant user or invalid password for login ' +request.form['login'])
			print('Unexistant user or invalid password for login ' +request.form['login'])
			return redirect('/login?from=' + from_page)
	else:	# méthode HTML GET
		return render_template('login.html', from_page=from_page)


@app.route('/register', methods=['GET', 'POST'])
def register():
	from_page = request.args.get('from', 'Main')
	if request.method == 'POST':
		if create(request.form['login'], request.form['password']):	# create a réussi (True)
			session['username'] = request.form['login']
			#session['name'] = escape(request.form['name'])              
			session['logged'] = True
			print('User creation successfull!')
			return redirect('/')		# on redirige à l'index
		else:		# create a échoué (False)
			flash('Creation fail: user \"'+ request.form['login'] + '\" already exists')
			print('Creation fail: user \"'+ request.form['login'] + '\" already exists')
			return redirect('/register?from=' + from_page)
	else:	# méthode HTML GET
		return render_template('register.html', from_page=from_page)


@app.route('/logout')
def logout():
    from_page = request.args.get('from', 'Main')
    session.clear()
    return redirect('/')
    #return redirect('/pages/' + from_page)


# ............................................................................................... #
if __name__ == '__main__':
	app.run(debug=True)
	app.logger.debug("Debug")
# ............................................................................................... #