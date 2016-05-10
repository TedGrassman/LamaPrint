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
	return hashlib.sha256(salted).hexdigest()

def authenticate(login, password):
	"""Authentifier un utilisateur"""
	db = engine.connect()
	try:
		name = db.execute(select([accounts.c.login]).where(accounts.c.login == login)).fetchone()
		if name is None:
			# L'utilisateur n'existe pas
			# code ...
			#return '**Authentication fail: login does not exist**'
			return False
		else:
			passhash = hash_for(password)
			storedHash = db.execute(select([accounts.c.password_hash]).where(accounts.c.login == login)).fetchone()
			if passhash == storedHash:
				#return '**Authentication successfull!**'
				return True
			else:
				#return '**Authentication fail: wrong password**'
				return False
	finally:
		db.close();

def create(login, password):
	"""Créer et enregistrer un utilisateur existant"""
	db = engine.connect()
	try:
		name = db.execute(select([accounts.c.login]).where(accounts.c.login == login)).fetchone()
		if name is None:
			# L'utilisateur n'existe pas ; on l'ajoute
			db.execute(accounts.insert(), [
				{'login': login, 'password_hash': hash_for(password)}
			])
			#return '**(New user)**'
			return True
		else:
			# L'utilisateur existe déjà ; erreur
			#return '**Creation fail: login already exists**'
			return False			
	finally:
		db.close();
				

@app.route('/')
@app.route('/index')
def index():
	return redirect(url_for('Page_HTML', filename='index.html'))

@app.route('/test')
def test():
	return "Hello !"

@app.route('/login', methods=['POST'])
def login():
	from_page = request.args.get('from', 'Main')
	if request.method == 'POST':
		if authenticate(request.form['login'], request.form['password']):	# le login a réussi (True)
			session['username'] = request.form['login']
			#session['name'] = escape(request.form['name'])              
			session['logged'] = True
			return redirect('/')		# on redirige à l'index
		else:		# authenticate a échoué (False)
			flash('Unexistant user or invalid password for login' +request.form['login'])
			return redirect('/login?from=' + from_page)
	else:	# méthode HTML GET
		return render_template('login.html', from_page=from_page)


@app.route('/register', methods=['POST'])
def register():
	from_page = request.args.get('from', 'Main')
	if request.method == 'POST':
		if create(request.form['login'], request.form['password']):	# create a réussi (True)
			session['username'] = request.form['login']
			#session['name'] = escape(request.form['name'])              
			session['logged'] = True
			return redirect('/')		# on redirige à l'index
		else:		# create a échoué (False)
			flash('Creation fail: user \"'+ request.form['login'] + '\" already exists')
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