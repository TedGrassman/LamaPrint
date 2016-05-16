# -*- coding:utf-8 -*-

from flask import *
from sqlalchemy import *
from sqlalchemy.sql import *
from sqlalchemy.orm import sessionmaker
from markdown import markdown
import os, hashlib
import random


app = Flask(__name__)

# Pour le hash du password
#app.secret_key = 'iswuygdedgv{&75619892__01;;>..zzqwQIHQIWS'
app.secret_key = os.urandom(256)
SALT = 'foo#BAR_{baz}^666'

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
	Column('creation_date', String),
	Column('score', Integer),
	Column('printer', String), #'yes' ou 'no'
	Column('birthdate', String),
	Column('telephone', String))

project = Table('project', metadata,
	Column('id', Integer, autoincrement = True, primary_key = True, nullable = False, unique = True),
	Column('creation_date', String),
	Column('user', String, ForeignKey('user.username', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('project_name', String),
	Column('score', Integer),
	Column('project_type', Integer), #'rquest', 'publication' ou 'offer'
	Column('description', Integer))

file = Table('file', metadata,
	Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
	Column('creation_date', String),
	Column('score', Integer),
	Column('project', Integer, ForeignKey('project.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('dimensions', String), # exemple: '3cmx4cm'
	Column('weight', Float),
	Column('price', String), # exemple: '€23.4'
	Column('name', String))
				
comment = Table('comment', metadata,
	Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
	Column('creation_date', String),
	Column('score', Integer),
	Column('project', Integer, ForeignKey('project.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('user', String, ForeignKey('user.username', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('comment_text', String))

metadata.create_all(engine)		# remplit la BdD avec les informations par défaut




def hash_for(password):
	salted = '%s @ %s' % (SALT, password)
	return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def authenticate(login, password):
	"""Authentifier un utilisateur"""
	db = engine.connect()
	try:
		result = db.execute(select([user.c.username]).where(user.c.username == login)).fetchone()
		
		if result is None:
			# L'utilisateur n'existe pas
			# code ...
			print('**Authentication fail: login does not exist**')
			return False
		else:
			name = result[0]
			print('User:', name)
			passhash = hash_for(password)
			#passhash = hash_for(password.encode('utf-8'))
			result = db.execute(select([user.c.password]).where(user.c.username == login)).fetchone()
			storedHash = result[0]
			print(login)
			print(password)
			#result = db.execute("select password_hash from user where login=\'"+login+"\'")
			"""for i in result:
				print(i)
				storedHash = i"""
			#storedHash = result.fetchone()[0]
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
		
def getUserInfo(username):
	db = engine.connect()
	try:
		result = db.execute(select([user]).where(user.c.username == username)).fetchone()
		if result is None:
			# L'utilisateur n'existe pas
			# code ...
			print('**Encounter problem getting user\'s info**')
			return False
		else:
			return result
	finally:
		db.close()

def create(login, password):
	"""Créer et enregistrer un utilisateur existant"""
	db = engine.connect()
	try:
		name = db.execute(select([user.c.username]).where(user.c.username == login)).fetchone()
		print(name)
		if name is None:
			# L'utilisateur n'existe pas ; on l'ajoute
			db.execute(user.insert(), [ {'username': login, 'password': hash_for(password)} ])
			print('**(New user)**')
			return True
		else:
			# L'utilisateur existe déjà ; erreur
			print('**Creation fail: login already exists**')
			return False
	finally:
		db.close();
		

def printer_create():
	engine = create_engine('sqlite:///lama.db', echo=True)
	try:
		Session=sessionmaker()
		Session.configure(bind=engine)
		db_session=Session()
		id=db_session.query(user.username).first()
		print('id= '+id)
		print('User:'+session.get('username'))
	finally:
		pass
	


"""Pour récupérer les ressource statiques contenues dans différents dossiers (autre que "static")"""
#os.path.join('js', path).replace('\\','/')
@app.route('/api/<path:somepath>')
def send_api(somepath):
	return send_from_directory('api', somepath)
@app.route('/bootstrap/<path:somepath>')
def send_bootstrap(somepath):
	return send_from_directory('bootstrap', somepath)
@app.route('/image/<path:somepath>')
def send_image(somepath):
	return send_from_directory('image', somepath)
@app.route('/jquery/<path:somepath>')
def send_jquery(somepath):
	return send_from_directory('jquery', somepath)
@app.route('/lamaprint.css')
def send_css():
	return url_for('static', filename='lamaprint.css')

@app.route('/')
@app.route('/index')
def index():
	data=request.cookies.get('logged')
	if data is None:
		session['logged']=False
		print('No cookie')
	return render_template('index.html', name="Main Page")

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
			response = make_response(render_template('index.html'))
			response.set_cookie('username', session['username'])
			
			flash('Authentication successfull')
			print('Authentication successfull')
			return response		# on redirige à l'index
		else:		# authenticate a échoué (False)
			flash('Unexistant user or invalid password for login ' +request.form['login'])
			print('Unexistant user or invalid password for login ' +request.form['login'])
			return redirect('/login?from=' + from_page)
	else:	# méthode HTML GET
		return render_template('login.html', name="Login", from_page=from_page)


@app.route('/register', methods=['GET','POST'])
def register():
	db = engine.connect()
	from_page=request.args.get('from', 'Main')
	if request.method == 'POST':
		if create(request.form['login'], request.form['password']):	# create a réussi (True)*
			session['username'] = request.form['login']
			session['name'] = escape(request.form['firstname'])
			if request.form['mail'] is not None:
				print("Add mail: "+request.form['mail']+" to DB")
				smt=user.update().values(name=request.form['mail']).where(user.c.username==request.form['login'])
				db.execute(smt)
			if request.form['firstname'] is not None:
				print("Add Firstname: "+request.form['firstname']+" to DB")
				smt=user.update().values(name=request.form['firstname']).where(user.c.username==request.form['login'])
				db.execute(smt)
			if request.form['lastname'] is not None:
				print("Add lastname: "+request.form['lastname']+" to DB")
				smt=user.update().values(lastname=request.form['lastname']).where(user.c.username==request.form['login'])
				db.execute(smt)
			if request.form['birthdate'] is not None:
				print("Add birthdate: "+request.form['birthdate']+" to DB")
				smt=user.update().values(birthdate=request.form['birthdate']).where(user.c.username==request.form['login'])
				db.execute(smt)
			if request.form['phonenumber'] is not None:
				print("Add phonenumber: "+request.form['phonenumber']+" to DB")
				smt=user.update().values(telephone=request.form['phonenumber']).where(user.c.username==request.form['login'])
				db.execute(smt)	
				
				session['logged'] = True
				response = make_response(render_template('index.html'))
				response.set_cookie('username', session['username'])
				print('User creation successfull!')
			
			return response		# on redirige à l'index
		else:		# create a échoué (False)
			flash('Creation fail: user \"'+ request.form['login'] + '\" already exists')
			print('Creation fail: user \"'+ request.form['login'] + '\" already exists')
			return redirect('/register?from=' + from_page)
	if request.method == 'GET':
		return render_template('register.html', name="Register", from_page=from_page)


@app.route('/logout')
def logout():
	from_page = request.args.get('from', 'Main')
	session.pop('logged_in', None)
	session.clear()
	return redirect('/')
	#return redirect('/pages/' + from_page)

@app.route('/profile/<username>', methods=['GET','POST'])	
def profile(username):
	if request.method=='GET':
		print(session.get('username'))
		result=getUserInfo(username)
		
		#Nom de Famille
		if result[3] is not None:
			nom=result[3]
		if result[3] is None:	
			nom='Non renseigné'
			
		#Prenom
		if result[4] is not None:
			prenom=result[4]
		if result[4] is None:	
			prenom='Non renseigné'
			
		#Date de naissance
		if result[9] is not None:
			birthdate=result[9]
		if result[9] is None:	
			birthdate='Non renseigné'
		
		return render_template("userpagetemplate.html",username=user,nom=nom,prenom=prenom, birthdate=birthdate)
				
				
@app.route('/propose')
def propose():
	db = engine.connect()
	if session['logged'] is False:
		return redirect('/')
	return render_template("propose.html")
	
@app.route('/rent', methods=['GET','POST'])
def rent():
	if request.method == 'POST':
		if session.get('logged') == False :
			print('User not connected')
			return render_template("rentprinter.html")
		
		else: 
			printer_create()
			
			return render_template("rentprinter.html")
			
	else:
		return render_template("rentprinter.html")

# ............................................................................................... #
if __name__ == '__main__':
	app.run(debug=True)
	app.logger.debug("Debug")
	pause
# ............................................................................................... #