# -*- coding:utf-8 -*-
from flask import *
from sqlalchemy import *
from sqlalchemy.sql import *
from sqlalchemy.orm import sessionmaker
from werkzeug import secure_filename
from markdown import markdown
import os, hashlib
import random
import datetime

app = Flask(__name__)

# Pour le hash du password
#app.secret_key = 'iswuygdedgv{&75619892__01;;>..zzqwQIHQIWS'
app.secret_key = os.urandom(256)
SALT = 'foo#BAR_{baz}^666'

# Création de la base de données
# Base de donnée : doit supporter les types "blob"
engine = create_engine('sqlite:///lama.db', echo=True)
metadata = MetaData()

# Pour l'upload de fichiers
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024		# taille max = 4Mo

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
	Column('ID', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),	
	Column('creation_date', String),
	Column('user', String, ForeignKey('user.username', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('dimensionsx', Float),
	Column('dimensionsy', Float),
	Column('dimensionsz', Float),
	Column('res', Integer),
	Column('price', Float), # exemple: '€23.4'
	Column('material', String),
	Column('address', String),
	Column('postcode', String),
	Column('city', String),
	Column('country', String))
				
comment = Table('comment', metadata,
	Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
	Column('creation_date', String),
	Column('score', Integer),
	Column('project', Integer, ForeignKey('project.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('user', String, ForeignKey('user.username', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('comment_text', String))

metadata.create_all(engine)		# remplit la BdD avec les informations par défaut


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def uploadFile(filepath="default"):
	""" Upload de fichier
		Exemple: pour uploader toto.jpg dans /uploads/test/ -> uploadFile("test")
		avec la dernière requête contenant un form qui contient un <input file>"""
	db = engine.connect()
	try:
		print("UPLOAD!")
		print("### upload du fichier", request.files['file'], "###")
		dirpath = os.path.join(app.config['UPLOAD_FOLDER'], filepath).replace('\\','/')
		if os.path.isdir(dirpath) is False:
			os.mkdir(dirpath)
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			path = os.path.join(dirpath, filename).replace('\\','/')
			print("Path =", path)
			file.save(path)
			
			return path

			#file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\','/'))
			#return redirect(url_for('uploaded_file', filename=filename))
	finally:
		db.close()


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
		db.close()
		
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

def getPrinterInfo(ID):
	db = engine.connect()
	print("### GetPrinterInfo, ID="+str(ID))
	try:
		result = db.execute(select([printer]).where(printer.c.ID == str(ID))).fetchone()
		if result is None:
			# L'imprimante n'existe pas
			# code ...
			print('**Encounter problem getting printer\'s info**')
			return False
		else:
			return result
	finally:
		db.close()


def getUserPrinter(username):
	db = engine.connect()
	print("### GetPrinterInfo, User="+username)
	try:
		result = db.execute(select([printer]).where(printer.c.user == username)).fetchone()
		if result is None:
			# L'imprimante n'existe pas
			# code ...
			print('**Encounter problem getting printer\'s info**')
			return False
		else:
			print(result)
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
		db.close()		


def printer_create(username, xyz, res, price, material, address):
	#engine = create_engine('sqlite:///lama.db', echo=True)
	db = engine.connect()
	"""try:
		Session=sessionmaker()
		Session.configure(bind=engine)
		db_session=Session()
		id=db_session.query(user.username).first()
		print('id= '+id)
		print('User:'+session.get('username'))

		db = engine.connect()
		try:

			idd = db.execute(printer.insert(),[{}])
			
		finally:
			db.close();
			return idd.lastrowid

	finally:
		pass"""
	try:
		print(datetime.datetime.now())
		db.execute(printer.insert(), [ {'user': username, 'creation_date': 'LOL', 'dimensionsx': xyz[0], 'dimensionsy': xyz[1], 'dimensionsz': xyz[2], 'res': res, 'price': price, 'material': material, 'address': address[0], 'postcode':address[1], 'city': address[2], 'country': address[3]} ] )
		return True
	finally:
		db.close()


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
@app.route('/uploads/<path:somepath>')
def send_uploads(somepath):
	return send_from_directory('uploads', somepath)

@app.route('/')
@app.route('/index')
def index():
	data=request.cookies.get('username')
	if data is None:
		session['logged']=False
		print('No cookie')
	else:
		session['logged']=True
		session['username']=data
	#data=request.cookies.get('logged')
	#if data is None:
	#	session['logged']=False				# fait systématiquement déconnecter la session...
	#	print('No cookie')
	return render_template('index.html', name="Main Page")

@app.route('/test')
def test():
	return "Hello !"

@app.route('/login', methods=['GET', 'POST'])
def login():

	print("### LOGIN ###")
	if request.method == 'POST':
		if authenticate(request.form['login'], request.form['password']):	# le login a réussi (True)
			session['username'] = request.form['login']
			#session['name'] = escape(request.form['name'])              
			session['logged'] = True
			response = make_response(redirect('/'))
			response.set_cookie('username', session['username'])
			
			#flash('Authentication successfull')
			print('Authentication successfull')
			return response		# on redirige à l'index
		else:		# authenticate a échoué (False)
			flash('Unexistant user or invalid password for login ' +request.form['login'])
			print('Unexistant user or invalid password for login ' +request.form['login'])
			return redirect('/login')
	else:	# méthode HTML GET
		return render_template('login.html', name="Login")


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
				smt=user.update().values(mail=request.form['mail']).where(user.c.username==request.form['login'])
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
			return redirect('/register')
	if request.method == 'GET':
		return render_template('register.html', name="Register")


@app.route('/logout')
def logout():
	from_page = request.args.get('from', 'Main')
	session.pop('logged_in', None)
	session.clear()
	resp = make_response(redirect('/'))
	resp.set_cookie('username', '', expires=0)
	return resp


@app.route('/editprofile/<username>', methods=['GET','POST'])
def editprofile(username):
	
	print("*****MODIFYPROFILE*****")
	data=request.cookies.get('username')
	print(data)
	if data is None:
			print('Pas de cookie')
			return redirect('/login')
	elif data==username:
		#rien
		print("data =", data, "; username =", username)
		
		if request.method == 'POST':
			
			db = engine.connect()
			print("POST editprofile")
			path = uploadFile("profile_images")
			if path is not None:
				image = "../"+path
				db.execute(user.update().values(profile_image_path = image).where(user.c.username == session.get('username')))
			else:
				image='../image/garou.png'
			print("IMAGE =", image)
			
			
			try:
				if request.form['firstname'] is not None:
					print("Add Firstname: "+request.form['firstname']+" to DB")
					smt=user.update().values(name=request.form['firstname']).where(user.c.username==username)
					db.execute(smt)
				if request.form['lastname'] is not None:
					print("Add lastname: "+request.form['lastname']+" to DB")
					smt=user.update().values(lastname=request.form['lastname']).where(user.c.username==username)
					db.execute(smt)
				if request.form['birthdate'] is not None:
					print("Add birthdate: "+request.form['birthdate']+" to DB")
					smt=user.update().values(birthdate=request.form['birthdate']).where(user.c.username==username)
					db.execute(smt)
				if request.form['mail'] is not None:
					print("Add mail: "+request.form['mail']+" to DB")
					smt=user.update().values(mail=request.form['mail']).where(user.c.username==username)
					db.execute(smt)
				if request.form['phonenumber'] is not None:
					print("Add phonenumber: "+request.form['phonenumber']+" to DB")
					smt=user.update().values(telephone=request.form['phonenumber']).where(user.c.username==username)
					db.execute(smt)
				
				# Mot de Passe !
				if request.form['newmdp'] is not None:
					newpassword = request.form['newmdp']
					password = request.form['mdp']
					passhash = hash_for(password)
					result = db.execute(select([user.c.password]).where(user.c.username == username)).fetchone()
					oldpasshash = result[0]
					if passhash==oldpasshash:
						newpasshash=hash_for(newpassword)
						print("Change password: "+newpassword+" to DB")
						smt=user.update().values(password=newpasshash).where(user.c.username==username)
						db.execute(smt)
					
			finally:
				db.close()

			return redirect("/profile/"+username)
			#return redirect(url_for('uploaded_file', filename=filename))

		else:
			print("GET editprofile")
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
			#Image de profil
			if result[6] is not None:
				image="../"+result[6]
			if result[6] is None:	
				image='../image/garou.png'		# image par défaut :)
			#print("IMAGE =", image)
			#Mail
			if result[2] is not None:
				mail=result[2]
			if result[2] is None:	
				mail='Non renseigné'
			#Phone
			if result[10] is not None:
				phone=result[10]
			if result[10] is None:	
				phone='NaN'

			return render_template("editprofile.html", name="Modifier le profil", username=username, nom=nom, prenom=prenom, birthdate=birthdate, image=image, mail=mail, phone=phone)


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

		#Image de profil
		if result[6] is not None:
			image="../"+result[6]
		if result[6] is None:	
			image='../image/garou.png'		# image par défaut :)
		print("FETCH USER : image =", image)
		#Mail
		if result[2] is not None:
			mail=result[2]
		if result[2] is None:	
			mail='lama@lamacorp.com'
		#Phone
		if result[10] is not None:
			phone=result[10]
		if result[10] is None:	
			phone='NaN'

		#Printer
		result=getUserPrinter(username)
		if result is not False:
			printerid=result[0]
		if result is False:	
			printerid=0

		return render_template("profile.html", name= "Profil", username=username, nom=nom, prenom=prenom, birthdate=birthdate, image=image, mail=mail, phone=phone,printerid=printerid)


@app.route('/demand', methods=['GET','POST'])
def demand():
	if request.method == 'GET':
		data=request.cookies.get('username')
		if data is None:
			print('Pas de cookie')
			return redirect('/login')
		else:
			return render_template("demand.html", name = "Demande de projet")
	if request.method == 'POST':
		db = engine.connect()
		session['username']=request.cookies.get('username')
		result = db.execute(select([project.c.project_name]).where(project.c.project_name==request.form['title'] and project.c.user==session['username'])).fetchone()
		if result is None:
			db.execute(project.insert(), [ {'project_name': request.form['title'], 'user':session['username'], 'description': request.form['description']}])
			print('create project')
			return redirect('/demand/'+request.form['title'])
		else:
			print('Vous avez déjà créé ce projet')
		return redirect('/')
		
		
@app.route('/demand/<title>', methods=['GET','POST'])
def demandDisplay(title):
	if request.method == 'GET':
		db = engine.connect()
		result = db.execute(select([project.c.description]).where(project.c.project_name==title and project.c.user==session['username'])).fetchone()
		if result is None:
			print('ERREUR BSD')
			return render_template("demand_display.html",name= "Demande:"+title, title=title)
		else:
			return render_template("demand_display.html",name= "Demande:"+title, title=title, description=result[0])


			
@app.route('/propose', methods=['GET','POST'])
def propose():
	db = engine.connect()
		
	if request.method == 'GET':
		data=request.cookies.get('username')
		if data is None:
			print('Pas de cookie')
			return redirect('/login')
		else:
			return render_template("propose.html", name = "Proposer un projet")
	
	if request.method == 'POST':
		session['username']=request.cookies.get('username')
		result = db.execute(select([file.c.project]).where(file.c.name==session['username'])).fetchone()
		#if result is None:
		#db.execute(project.insert(), [ {'project_name': request.form['title'], 'user':session['username']}])
		print('create project')
		return redirect('/project/'+request.form['title'])
		#else:
		#	print('Vous avez déjà créé ce projet')
		return redirect('/')
		
@app.route('/project/<title>')
def project(title):
	db = engine.connect()
		
	if request.method == 'GET':
		return render_template("project.html", title=title)
	if session.get('logged') is False:
		return redirect('/login')
	return render_template("propose.html")

@app.route('/projet')
def projet():
	return render_template("projet.html")


@app.route('/printers', methods=['GET','POST'])
def printers():
	db = engine.connect()

	if request.method == 'POST':
		s = "select * from printer where "
		prev = 0
		if request.form['dimxmax']:
			s = s + "dimensionsx >= " + request.form['dimxmax']
			prev = 1
		if request.form['dimymax']:
			if prev == 1:
				s = s + " and "
			s = s + "dimensionsy >= " + request.form['dimymax']
			prev = 1
		if request.form['dimzmax']:
			if prev == 1:
				s = s + " and "
			s = s + "dimensionsz >= " +  request.form['dimzmax']
			prev = 1
		if request.form['resolution']:
			if prev == 1:
				s = s + " and "
			s = s + "res <= " + "\"" + request.form['resolution'] + "\""
			prev = 1
		if request.form['prix']:
			if prev == 1:
				s = s + " and "
			s = s + "price <= " + "\"" + request.form['prix'] + "\""
			prev = 1
		if request.form['codepostal']:
			if prev == 1:
				s = s + " and "
			s = s + "postal_code = " + "\"" + request.form['codepostal'] + "\""
			prev = 1
		if request.form['ville']:
			if prev == 1:
				s = s + " and "
			s = s + "city = " + "\"" + request.form['ville'] + "\""
			prev = 1
		if request.form['pays']:
			if prev == 1:
				s = s + " and "
			s = s + "country = " + "\"" + request.form['pays'] + "\""
			prev = 1
		
		if prev == 0:
			print("Empty request")
		else:
			print("Request made: ")
			#s = "select * from printer"
			print(s)
			if db.execute(s) is None:
				s2="Aucun r."
				#message = Markup(s2)
				#flash(message)

			for row in db.execute(s):
				print(row)
				s = "----------------------------------------------------------<br /><b><a href=\"/printer/"
				s=s+str(row.ID)
				s=s+"\">Imprimante de "
				s=s+row.user
				s=s+"</a></b> <br />"
				s=s+"<b>Résolution</b> : "
				s=s+str(row.res)
				s=s+" µm <br /> <b>Taille maximale</b> : "
				s=s+str(row.dimensionsx)
				s=s+" x "
				s=s+str(row.dimensionsy)
				s=s+" x "
				s=s+str(row.dimensionsz)+" cm<br />"
				s=s+"<b>Prix min</b> : "+str(row.price)+" €/kg<br />"
				s=s+"<b>Ville</b> : "+row.city+", "+row.country+" <br /><br />"
				message = Markup(s)
				flash(message)
			print('\n')
			
		redirect('/printers')
	else:
		return render_template('printers.html')

@app.route('/searchproject', methods=['GET','POST'])
def searchproject():
	db = engine.connect()
	if request.method == 'POST':
		s = "select * from project where "
		prev = 0
		if request.form['dimxmax']:
			s = s + "dimensionsx <= " + "\"" + request.form['dimxmax'] + "\""
			prev = 1
		if request.form['dimymax']:
			if prev == 1:
				s = s + " and "
			s = s + "dimensionsy <= " + "\"" + request.form['dimymax'] + "\""
			prev = 1
		if request.form['dimzmax']:
			if prev == 1:
				s = s + " and "
			s = s + "dimensionsz <= " + "\"" + request.form['dimzmax'] + "\""
			prev = 1
		if request.form['field']:
			if prev == 1:
				s = s + " and "
			s = s + "description like " + "\"%" + request.form['field'] + "%\""
			prev = 1
		if request.form['prix']:
			if prev == 1:
				s = s + " and "
			s = s + "price <= " + "\"" + request.form['prix'] + "\""
			prev = 1

		if prev == 0:
			print("Empty request")
		else:
			print("Request made: ")
			print(s)

			for row in db.execute(s):
				print(row)
			print('\n')
	return render_template('searchproject.html')


@app.route('/printer/<id>')
def showprinter(id):
	
	id = int(id)
	result=getPrinterInfo(id);
	print("### /printer, result=", result)

	username="Aucun"
	nom=prenom='Non renseigné'
	phone='NaN'
	x=y=z=0
	res=price=0
	material=address=postcode=city=country="Non renseigné"

	
	if result is not False:
		#User
		if result[2] is not None:
			username=result[2]
		if result[2] is None:	
			username='Non renseigné'
		userInfo=getUserInfo(username)
		if userInfo is not False:
			#Nom de Famille
			if userInfo[3] is not None:
				nom=userInfo[3]
			if userInfo[3] is None:	
				nom='Non renseigné'
			#Prenom
			if userInfo[4] is not None:
				prenom=userInfo[4]
			if userInfo[4] is None:	
				prenom='Non renseigné'
			#Phone
			if userInfo[10] is not None:
				phone=userInfo[10]
			if userInfo[10] is None:	
				phone='NaN'

		#x
		if result[3] is not None:
			x=result[3]
		if result[3] is None:	
			x='Non renseigné'
		#y
		if result[4] is not None:
			y=result[4]
		if result[4] is None:	
			y='Non renseigné'
		#z
		if result[5] is not None:
			z=result[5]
		if result[5] is None:	
			z='Non renseigné'
		#Résolution
		if result[6] is not None:
			res=result[6]
		if result[6] is None:
			res='Non renseigné'
		#Prix
		if result[7] is not None:
			price=result[7]
		if result[7] is None:	
			price='Non renseigné'
		#Matière
		if result[8] is not None:
			material=result[8]
		if result[8] is None:	
			material='Non renseigné'
		#Adresse
		if result[9] is not None:
			address=result[9]
		if result[9] is None:	
			address='Non renseigné'
		#Code postal
		if result[10] is not None:
			postcode=result[10]
		if result[10] is None:	
			postcode='Non renseigné'
		#Ville
		if result[11] is not None:
			city=result[11]
		if result[11] is None:	
			city='Non renseigné'
		#Pays
		if result[12] is not None:
			country=result[12]
		if result[12] is None:	
			country='Non renseigné'

	return render_template('printer.html', name=" Imprimante n°"+str(id), username=username, prenom=prenom, nom=nom, x=x, y=y, z=z, res=res, price=price, material=material, address=address, postcode=postcode, city=city, country=country, phone=phone)


@app.route('/rent', methods=['GET','POST'])
def rent():
	username=request.cookies.get('username')
	print(username)
	if username is None:
		print('Pas de cookie')
		return redirect('/login')
	else:
		if request.method == 'POST':
				xyz = (request.form['dimxmax'], request.form['dimymax'], request.form['dimzmax'])
				res = request.form['resolution']
				price = request.form['prix']
				material = request.form['materiaux']
				address = (request.form['adresse'], request.form['codepostal'], request.form['ville'], request.form['pays'])
				print("### /rent : printer_create")
				printer_create(username=username, xyz=xyz, res=res, price=price, material=material, address=address)
				return redirect('/rent')
				
		else:
			return render_template("rentprinter.html")

"""	
@app.route('/rent', methods=['GET','POST'])
def rent():		
	if request.cookies.get('username') is None:
		print('User not connected')
		return redirect('/login')

	else: 				
		
		if request.method == 'POST':
			db = engine.connect()
			idd=printer_create()
			
			print("idd ",idd)
			if idd>0 :	
				
				print("Add name :"+ request.cookies.get('username'))
				smt=printer.update().values(user=request.cookies.get('username')).where(printer.c.ID==idd)
				db.execute(smt)
				
				print("Add creation_date :"+ str(datetime.date.today()))
				smt=printer.update().values(creation_date=str(datetime.date.today())).where(printer.c.ID==idd)
				db.execute(smt)
				
				if request.form['dimxmax'] is not None :
					print("Add dimensions: "+request.form['dimxmax'])
					smt=printer.update().values(dimensionsx=request.form['dimxmax']).where(printer.c.ID==idd)
					db.execute(smt)
				if request.form['dimymax'] is not None :
					print("Add dimensions: "+request.form['dimymax'])
					smt=printer.update().values(dimensionsy=request.form['dimymax']).where(printer.c.ID==idd)
					db.execute(smt)
				if request.form['dimzmax'] is not None :
					print("Add dimensions: "+request.form['dimzmax'])
					smt=printer.update().values(dimensionsz=request.form['dimzmax']).where(printer.c.ID==idd)
					db.execute(smt)	
					
				if request.form['resolution'] is not None:
					print("Add resolution: "+request.form['resolution']+" to DB")
					smt=printer.update().values(res=request.form['resolution']).where(printer.c.ID==idd)
					db.execute(smt)
				if request.form['prix'] is not None:
					print("Add price: "+request.form['prix']+" to DB")
					smt=printer.update().values(price=request.form['prix']).where(printer.c.ID==idd)
					db.execute(smt)
				if request.form['materiaux'] is not None:
					print("Add material: "+request.form['materiaux']+" to DB")
					smt=printer.update().values(material=request.form['materiaux']).where(printer.c.ID==idd)
					db.execute(smt)
				if request.form['adresse'] is not None:
					print("Add address: "+request.form['adresse']+" to DB")
					smt=printer.update().values(address=request.form['adresse']).where(printer.c.ID==idd)
					db.execute(smt)
				if request.form['codepostal'] is not None:
					print("Add postcode: "+request.form['codepostal']+" to DB")
					smt=printer.update().values(postcode=request.form['codepostal']).where(printer.c.ID==idd)
					db.execute(smt)
				if request.form['ville'] is not None:
					print("Add city: "+request.form['ville']+" to DB")
					smt=printer.update().values(city=request.form['ville']).where(printer.c.ID==idd)
					db.execute(smt)
				if request.form['pays'] is not None:
					print("Add country: "+request.form['pays']+" to DB")
					smt=printer.update().values(country=request.form['pays']).where(printer.c.ID==idd)
					db.execute(smt)
						
					print('Printer creation successful!')
					
					for row in db.execute('select * from printer'):
						print(row)
					print('\n')
					
					return render_template("rentprinter.html")
					
			else:
				print('Printer creation failed')
				return render_template("rentprinter.html")	
		else:
			return render_template("rentprinter.html")	
"""

# ............................................................................................... #
if __name__ == '__main__':
	app.run(debug=True)
	app.logger.debug("Debug")
# ............................................................................................... #
