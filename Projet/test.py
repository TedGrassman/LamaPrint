# -*- coding:utf-8 -*-
from flask import *
from sqlalchemy import *
from sqlalchemy.sql import *
from sqlalchemy.orm import sessionmaker
from werkzeug import secure_filename
from markdown import markdown
import os, hashlib
import random
import re
import datetime

app = Flask(__name__)


#____________________________________________________________#
#____________________________________________________________#
#			INITIALISATION
#____________________________________________________________#
#____________________________________________________________#


# Pour le hash du password
#app.secret_key = 'iswuygdedgv{&75619892__01;;>..zzqwQIHQIWS'
app.secret_key = os.urandom(256)
SALT = 'foo#BAR_{baz}^666'

# Pour l'upload de fichiers
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024		# taille max = 4Mo
uploadpath = os.path.join(app.config['UPLOAD_FOLDER']).replace('\\','/')
if os.path.isdir(uploadpath) is False:
	os.mkdir(uploadpath)


#____________________________________________________________#
#		DATABASE INITIALISATION
#____________________________________________________________#

# Création de la base de données
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
	Column('user', String, ForeignKey('user.username', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('parent_project', Integer, ForeignKey('project.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('creation_date', String),
	Column('project_name', String),
	Column('project_type', Integer), #'rquest', 'publication' ou 'offer'
	Column('score', Integer),
	Column('dimensionsx', Integer),
	Column('dimensionsy', Integer),
	Column('dimensionsz', Integer),
	Column('image_path', String),
	Column('price', Integer),
	Column('description', String))

file = Table('file', metadata,
	Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
	Column('project', Integer, ForeignKey('project.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('creation_date', String),
	Column('score', Integer),
	Column('file_path', String),
	Column('image_path', String),
	Column('dimensionsx', Integer),
	Column('dimensionsy', Integer),
	Column('dimensionsz', Integer),
	Column('weight', Float),
	Column('price', Integer))
	
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
	Column('country', String),
	Column('description', String))
				
comment = Table('comment', metadata,
	Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
	Column('creation_date', String),
	Column('score', Integer),
	Column('project', Integer, ForeignKey('project.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('user', String, ForeignKey('user.username', ondelete = 'SET NULL', onupdate = 'CASCADE')),
	Column('comment_text', String))

metadata.create_all(engine)		# remplit la BdD avec les informations par défaut



#____________________________________________________________#
#____________________________________________________________#
#			Fonctions annexes
#____________________________________________________________#
#____________________________________________________________#


#____________________________________________________________#
#		UPLOAD MANAGEMENT
#____________________________________________________________#

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def uploadFile(request, filestr, filepath="default"):
	""" Upload de fichier
		Exemple: pour uploader toto.jpg dans /uploads/test/ -> uploadFile("test")
		avec la dernière requête contenant un form qui contient un <input file>"""
	db = engine.connect()
	try:
		print("UPLOAD!")
		file = request.files[filestr]
		print("### upload du fichier", file, "###")
		dirpath = os.path.join(app.config['UPLOAD_FOLDER'], filepath).replace('\\','/')
		if os.path.isdir(dirpath) is False:
			os.mkdir(dirpath)
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


#____________________________________________________________#
#		PASSWORD & USER MANAGEMENT
#____________________________________________________________#

def hash_for(password):
	salted = '%s @ %s' % (SALT, password)
	return hashlib.sha256(salted.encode('utf-8')).hexdigest()


def isUserLogged(username, request):
	print("??? Is " +username+ " logged ???")
	user=request.cookies.get('username')
	print("request.cookies.get('username') =", user)
	if(user==username):
		session['logged']=True
		session['username']=username
		return True
	else:
		return False

def getUserName(request):
	username=request.cookies.get('username')
	print("??? Is any user logged ???")
	print("Current User =", username)
	if username is None:
		print('Pas de cookie')
	elif username is not None:
		session['logged']=True
		session['username']=username
	return username


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


#____________________________________________________________#
#		PRINTER MANAGEMENT
#____________________________________________________________#

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

def printer_create(username, xyz, res, price, material, address, description):
	#engine = create_engine('sqlite:///lama.db', echo=True)
	db = engine.connect()
	try:
		print(datetime.datetime.now())
		idd = db.execute(printer.insert(), [ {'user': username, 'creation_date': str(datetime.date.today()) , 'dimensionsx': xyz[0], 'dimensionsy': xyz[1], 'dimensionsz': xyz[2], 'res': res, 'price': price, 'material': material, 'address': address[0], 'postcode':address[1], 'city': address[2], 'country': address[3], 'description': description } ])
		return idd.lastrowid
	finally:
		db.close()


#____________________________________________________________#
#		PROJECT & FILE MANAGEMENT
#____________________________________________________________#

def getProjectInfo(title):
	db = engine.connect()
	print("### GetProjectInfo, title = "+title)
	try:
		result = db.execute(select([project]).where(project.c.project_name == title)).fetchone()
		if result is None:
			# Le projet n'existe pas
			# code ...
			print('**Encounter problem getting project\'s info**')
			return False
		else:
			return result
	finally:
		db.close()

def getFileInfo(idd):
	db = engine.connect()
	print("### GetFileInfo, title = "+str(idd))
	try:
		result = db.execute(select([file]).where(file.c.id == idd)).fetchone()
		if result is None:
			# Le fichier n'existe pas
			# code ...
			print('**Encounter problem getting file\'s info**')
			return False
		else:
			return result
	finally:
		db.close()

def getProjectFile(title):
	db = engine.connect()
	print("### getProjectFile, title = "+title)
	try:
		# id du projet
		idd = db.execute(select([project.c.id]).where(project.c.project_name == title)).fetchone()
		print("ID du projet =", idd, type(idd))
		# fichiers correspondant
		idd = idd[0]
		result = db.execute(select([file]).where(file.c.project == idd)).fetchall()
		if result is None:
			# Aucun fichier
			# code ...
			print('**Encounter problem getting file\'s info**')
			return False
		else:
			print(result)
			for row in result:
				print(row)
			return result
	finally:
		db.close()


#____________________________________________________________#
#____________________________________________________________#
# Fonctions gestionnaires de routes
#____________________________________________________________#
#____________________________________________________________#


#____________________________________________________________#
#		STATIC RESOURCES
#____________________________________________________________#

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


#____________________________________________________________#
#		GLOBAL AND TEST
#____________________________________________________________#

@app.route('/')
@app.route('/index')
def index():
	username = getUserName(request)
	return render_template('index.html', name="Main Page")

@app.route('/test')
def test():
	return "Hello !"


#____________________________________________________________#
#		USER MANAGEMENT
#____________________________________________________________#

@app.route('/login', methods=['GET', 'POST'])
def login():
	print("### LOGIN ###")
	username = getUserName(request)
	if username is not None:
		return(redirect('/'))
	else:
		if request.method == 'POST':
			if authenticate(request.form['login'], request.form['password']):	# le login a réussi (True)
				session['username'] = request.form['login']
				#session['name'] = escape(request.form['name'])              
				session['logged'] = True
				response = make_response(redirect('/'))
				response.set_cookie('username', session['username'])
				
				flash('Authentication successfull ! Welcome back, '+request.form['login']+ ' =)', 'success')
				print('Authentication successfull ! Welcome back, '+request.form['login'])
				return response		# on redirige à l'index
			else:		# authenticate a échoué (False)
				flash('Unexistant user or invalid password for login ' +request.form['login'], 'danger')
				print('Unexistant user or invalid password for login ' +request.form['login'])
				return redirect('/login')
		else:	# méthode HTML GET
			return render_template('login.html', name="Login")


@app.route('/register', methods=['GET','POST'])
def register():
	
	username = getUserName(request)
	if username is not None:
		flash('You must log out to register as a new user', 'info')
		return(redirect('/'))
	else:
		db = engine.connect()
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
				response = make_response(redirect('/'))
				response.set_cookie('username', session['username'])
				flash('User creation successfull ! Welcome, '+request.form['login']+ ' =)', 'success')
				print('User creation successfull ! Welcome, '+request.form['login']+ ' =)')
				return response		# on redirige à l'index

			else:		# create a échoué (False)
				flash('Creation fail: user \"'+ request.form['login'] + '\" already exists', 'danger')
				print('Creation fail: user \"'+ request.form['login'] + '\" already exists')
				return redirect('/register')
		if request.method == 'GET':
			return render_template('register.html', name="Register")


@app.route('/logout')
def logout():
	session.pop('logged', None)
	session.clear()
	flash('You have been successfully logged out. See you soon !', 'info')
	resp = make_response(redirect('/'))
	resp.set_cookie('username', '', expires=0)
	return resp


@app.route('/profile/<username>', methods=['GET','POST'])	
def profile(username):
	if request.method=='GET':
		print(session.get('username'))
		result=getUserInfo(username)
		
		if result is False:
			flash('Error: user \"'+ username + '\" may not exist.', 'warning')
			print('Error: user \"'+ username + '\" may not exist.')
			return redirect('/')

		else:
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


@app.route('/editprofile/<username>', methods=['GET','POST'])
def editprofile(username):
	
	print("*****MODIFYPROFILE*****")
	userLogged = isUserLogged(username, request)
	if userLogged is False:
			print('Pas de cookie')
			flash('You must log in as correct user to edit your profile', 'info')
			return redirect('/login')
	elif userLogged is True:

		if request.method == 'POST':
			
			db = engine.connect()

			print("POST editprofile")
			path = uploadFile(request, "file", filepath="profile_images")
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
				if request.form.get('newmdp') is not "" and request.form.get('mdp') is not "":		# les champs ne sont jamais None mais plutôt ""
					print("##### CHANGE PASSWORD ASKED #####")
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
						flash('Your password has been successfully changed', 'success')
					else:
						print("Password changed failed : wrong old password")
						flash("Password changed failed : wrong old password", 'warning')

				# Suppression de compte !!
				#print("request.form.get('DeletionCheckbox') =", request.form.get('DeletionCheckbox'))	# None or value=valeur
				if request.form.get('DeletionCheckbox') is not None:
					print("##### ! DELETION ASKED ! #####")
					password = request.form['delconfirm']
					passhash = hash_for(password)
					result = db.execute(select([user.c.password]).where(user.c.username == username)).fetchone()
					storedpasshash = result[0]
					print(passhash)
					print(storedpasshash)
					if passhash==storedpasshash:
						print("! Correct password, deletion authorized !")
						smt = user.delete(user).where(user.c.username==username)
						print("user.delete(user).where(user.c.username==username) =", smt)
						print(db.execute(smt))
						print("##### ! DELETION COMPLETE ! #####")
						flash("Your account has been successfully deleted", 'danger')
						session.pop('logged', None)
						session.clear()
						resp = make_response(redirect('/'))
						resp.set_cookie('username', '', expires=0)
						return(resp)		# on déconnecte l'utilisateur, car sa page n'existe plus
					else:
						print("! Account deletion failed : wrong password !")
						flash("Account deletion failed : wrong password", 'warning')
						return redirect("/profile/"+username)
					
			finally:
				db.close()

			flash("Your informations have been successfully updated", 'success')
			return redirect("/profile/"+username)
			#return redirect(url_for('uploaded_file', filename=filename))

		else:
			print("GET editprofile")
			print(session.get('username'))
			result=getUserInfo(username)
			
			if result is False:
				flash('Error: user \"'+ username + '\" may not exist.', 'warning')
				print('Error: user \"'+ username + '\" may not exist.')
				return redirect('/')

			else:
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


#____________________________________________________________#
#		PRINTER MANAGEMENT
#____________________________________________________________#

@app.route('/rent', methods=['GET','POST'])
def rent():
	username = getUserName(request)
	if username is None:
			print('Pas de cookie')
			flash('You must log in to rent your printer', 'info')
			return redirect('/login')
	elif username is not None:
		if request.method == 'POST':
			xyz = (request.form['dimxmax'], request.form['dimymax'], request.form['dimzmax'])
			res = request.form['resolution']
			price = request.form['prix']
			material = request.form['materiaux']
			address = (request.form['adresse'], request.form['codepostal'], request.form['ville'], request.form['pays'])
			description = request.form['description']
			print("### /rent : printer_create")
			idd=printer_create(username=username, xyz=xyz, res=res, price=price, material=material, address=address, description=description)
			print("idd =",idd)
			if(idd > 0):
				flash('Printer n°'+ str(idd) + ' has been successfully rented.', 'success')
				return redirect('/printer/'+str(idd))
			else:
				return(redirect('/rent'))

		else:
			return render_template("rentprinter.html", name="Proposer mon imprimante 3D")


@app.route('/printer/<idd>')
def showprinter(idd):
	
	idd = int(idd)
	result=getPrinterInfo(idd);
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
			country=country.upper()
		if result[12] is None:	
			country='Non renseigné'
		#Description
		if result[13] is not None:
			description=result[13]
		if result[13] is None:	
			description='-- Aucune description --'

		return render_template('printer.html', name=" Imprimante n°"+str(idd), username=username, prenom=prenom, nom=nom, x=x, y=y, z=z, res=res, price=price, material=material, address=address, postcode=postcode, city=city, country=country, phone=phone, description=description)

	elif result is False:
		flash('Error: printer n°'+ str(idd) + ' may not exist.', 'warning')
		print('Error: printer n°'+ str(idd) + ' may not exist.')
		return redirect('/')


#____________________________________________________________#
#		PROJECT MANAGEMENT
#____________________________________________________________#

@app.route('/demand', methods=['GET','POST'])
def demand():
	username = getUserName(request)
	if username is None:
			print('Pas de cookie')
			flash('You must log in to make a demand', 'info')
			return redirect('/login')
	elif username is not None:
		
		if request.method == 'GET':
			return render_template("demand.html", name = "Demande de projet")
		elif request.method == 'POST':
			db = engine.connect()
			print("## DEMAND CREATION")
			result = db.execute(select([project.c.project_name]).where(project.c.project_name==request.form['title'])).fetchone()
			if result is None:
				idd = db.execute(project.insert(), [ {'project_name': request.form['title'], 'creation_date': str(datetime.date.today()), 'user': username, 'description': request.form['description'], 'project_type': 1}])
				fichier = request.files["images"]
				print("Fichier =", fichier)
				print("type(fichier) =", type(fichier))
				path = uploadFile(request, "images", filepath="project_images")
				if path is not None:
					image = "../"+path
				else:
					image='../image/lama.png'
				db.execute(project.update().values(image_path = image).where(project.c.project_name == request.form['title']))
				print("IMAGE =", image)

				print('### DEMAND CREATED ###')
				flash('Demand ' +request.form['title']+ ' has been succefully created', 'success')
				return redirect('/demand/'+request.form['title'])
			else:
				flash('Demand creation failed: ' +request.form['title']+ ' may already exist', 'danger')
				print('Vous avez déjà créé ce projet')
				return redirect('/demand')
		
		
@app.route('/demand/<title>', methods=['GET','POST'])
def demandDisplay(title):
	if request.method == 'GET':
		db = engine.connect()
		#description = db.execute(select([project.c.description]).where(project.c.project_name==title)).fetchone()
		#img = db.execute(select([project.c.image_path]).where(project.c.project_name==title)).fetchone()
		result = getProjectInfo(title)
		print(result)
		
		if result is False:
			flash('Error: project \"'+ title + '\" may not exist.', 'warning')
			print('Error: project \"'+ title + '\" may not exist.')
			return redirect('/')
		else:
			#ID
			if result[0] is not None:
				idd=result[0]
			if result[0] is None:	
				idd=0
			#User
			if result[1] is not None:
				user=result[1]
			if result[1] is None:	
				user='Non renseigné'
			#Image
			if result[10] is not None:
				image=result[10]
			if result[10] is None:	
				image='../image/lama.png'
			#Description
			if result[12] is not None:
				description=result[12]
			if result[12] is None:	
				description='-- Aucune description --'

			l=getCom(title)
			l.reverse()

			return render_template("demand_display.html", name= "Demande : "+title, id=idd, username=user, title=title, description=description, list=l, image=image)
	

@app.route('/propose', methods=['GET','POST'])
def propose():

	username = getUserName(request)
	
	if username is None:
		print('Pas de cookie')
		flash('You must log in to propose a project', 'info')
		return redirect('/login')
	
	elif username is not None:
		if request.method == 'GET':
				return render_template("propose.html", name = "Proposer une imprimante")
		if request.method == 'POST':
			db = engine.connect()
			print("## PROPOSE CREATION")
			result = db.execute(select([project.c.id]).where(project.c.project_name==request.form['title'])).fetchone()
			if result is None:
				idd = db.execute(project.insert(), [ {'project_name': request.form['title'], 'creation_date': str(datetime.date.today()), 'user': username, 'description': request.form['description'], 'project_type':2}])
				idd=idd.lastrowid
				path = uploadFile(request, "images", filepath="project_images")
				if path is not None:
					image = "../"+path
				else:
					image='../image/lama.png'
				db.execute(project.update().values(image_path = image).where(project.c.id == idd))
				print("IMAGE =", image)

				i=request.form['nbfiles']
				i=int(i)
				print("Nombre de fichiers :", i)

				for j in range(i):
					#CREATION DES FICHIERS
					fidd = db.execute(file.insert(), [{'project': idd, 'creation_date': str(datetime.date.today()), 'price':request.form['prix'], 'weight':request.form['masse'], 'dimensionsx':request.form['dimx'],'dimensionsy':request.form['dimy'],'dimensionsx':request.form['dimz']}])
					fidd=fidd.lastrowid
					#UPLOAD DES FICHIERS
					path = uploadFile(request, "fichier"+str(j), filepath="CAO")
					if path is not None:
						fichier = "../"+path
					else:
						fichier = ""	# chemin vide -> aucun fichier. Normalement, n'arrive pas !
					db.execute(file.update().values(file_path = fichier).where(file.c.id == fidd))
					print("FICHIER =", fichier)
					db.execute(file.update().values(image_path = image).where(file.c.id == fidd))
				

				print('### PROJECT CREATED ###')
				flash('Project ' +request.form['title']+ 'has been succefully created', 'success')
				return redirect('/project_display/'+request.form['title'])
			else:
				print('Vous avez déjà créé ce projet')
				flash('Project creation failed: ' +request.form['title']+ ' may already exist', 'danger')
				return redirect("/project_display/"+request.form['title'])
			db.close()

	
@app.route('/project_display/<title>')
def projectDisplay(title):
	db = engine.connect()
	if request.method == 'GET':
		project = getProjectInfo(title)
		files = getProjectFile(title)
		print("Project =", project)
		print("Files =", files)

		for row in files:
			print(row)

		if project is False:
			flash('Error: project \"'+ title + '\" may not exist.', 'warning')
			print('Error: project \"'+ title + '\" may not exist.')
			return redirect('/')
		else:
			#User
			if project[1] is not None:
				user=project[1]
			if project[1] is None:	
				user='Non renseigné'
			#Image
			if project[10] is not None:
				image=project[10]
			if project[10] is None:	
				image='../image/lama.png'
			#Description
			if project[12] is not None:
				description=project[12]
			if project[12] is None:	
				description='-- Aucune description --'
		
			l=getCom(title)
			l.reverse()

			# A améliorer, notamment dans le template !! (c'est pas top...)
			if files == []:
				print('Aucun fichier pour le project \"'+ title + '\".')
				return render_template("project_display.html", name="Projet "+title, username=user, title=title, image=image, description=description, id=0, dimx=0, dimy=0, dimz=0, prix=0, masse=0, list=l, userfile="")
			else:
				for row in files:
					f=row
				return render_template("project_display.html", name="Projet "+title, username=user, title=title, image=image, description=description, id=f[0], dimx=f[6], dimy=f[7], dimz=f[8], prix=f[10], masse=f[9], list=l)
	#if session.get('logged') is False:
	#	return redirect('/login')
	#return redirect('/propose')
			

	
@app.route('/projet')
def projet():
	return render_template("projet.html")


#____________________________________________________________#
#		SEARCH MANAGEMENT
#____________________________________________________________#

@app.route('/searchprinter', methods=['GET','POST'])
def searchprinter():
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
			s = s + "res <= " + request.form['resolution']
			prev = 1
		if request.form['prix']:
			if prev == 1:
				s = s + " and "
			s = s + "price <= " + request.form['prix']
			prev = 1
		if request.form['codepostal']:
			if prev == 1:
				s = s + " and "
			s = s + "postcode = " + "\"" + request.form['codepostal'] + "\""
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
			result = db.execute(s)
			print(result)
			if db.execute(s).first() is None:
				s2="<strong>Aucun résultat</strong>"
				print("## SEARCH : NO RESULTS")
				message = Markup(s2)
				flash(message)

			for row in result:
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
				s=s+"<b>Ville</b> : "+row.city+", "+row.country.upper()+" <br /><br />"
				message = Markup(s)
				flash(message)
			print('\n')
			
		return(redirect('/searchprinter'))
	else:
		return render_template('searchprinter.html', name="Recherche d'imprimante 3D")

@app.route('/searchproject', methods=['GET','POST'])
def searchproject():
	db = engine.connect()
	if request.method == 'POST':
		s = "select * from project where "
		prev = 0
		if request.form['dimxmax']:
			s = s + "dimensionsx <= " +  request.form['dimxmax']
			prev = 1
		if request.form['dimymax']:
			if prev == 1:
				s = s + " and "
			s = s + "dimensionsy <= " + request.form['dimymax']
			prev = 1
		if request.form['dimzmax']:
			if prev == 1:
				s = s + " and "
			s = s + "dimensionsz <= " + request.form['dimzmax']
			prev = 1
		if request.form['field']:
			if prev == 1:
				s = s + " and "
			s = s + "description like " + "\"%" + request.form['field'] + "%\""
			prev = 1
		if request.form['prix']:
			if prev == 1:
				s = s + " and "
			s = s + "price <= " + request.form['prix']
			prev = 1

		if prev == 0:
			print("Empty request")
			s3="<strong>Requête vide !</strong> Veuillez entrer des paramètres."
			message = Markup(s3)
			flash(message)
		else:
			print("Request made: ")
			#s = "select * from printer"
			print(s)
			result = db.execute(s)
			print(result)
			if db.execute(s).first() is None:
				print("## SEARCH : NO RESULTS")
				s2="<strong>Aucun résultat</strong>"
				message = Markup(s2)
				flash(message)

			for row in result:
				print(row)
				s = "----------------------------------------------------------<br/><b><a href=\"/project_display/"
				s=s+row.project_name
				s=s+"\">"
				s=s+row.project_name+ "</a> (par <a href=\"/profile/"
				s=s+row.user
				s=s+"\">" + row.user
				s=s+"</a>)</b> <br />"
				s=s+"<b>Description</b> : "
				s=s+row.description
				if row.image_path is not None:
					s=s+"<br /> <b>Image: </b><a href=\""
					s=s+row.image_path
					s=s+"\">"
					s=s+"voir l\'image" + "</a>"
				s=s+"<br/><br/>"
				message = Markup(s)
				flash(message)
			print('\n')
		return(redirect('/searchproject'))
	else:
		return render_template('searchproject.html', name="Recherche de projet")


#____________________________________________________________#
#		COMMENTS MANAGEMENT
#____________________________________________________________#

@app.route('/write_comment/<title>',methods=['GET','POST'])
def writeCom(title):
	print("### WRITE COM ! ###")
	username=getUserName(request)
	value = request.args.get('key')
	db = engine.connect()
	#get project id
	result = db.execute(select([project.c.id]).where(project.c.project_name==title)).fetchone()
	idd = result[0]
	print(type(idd), idd)
	stridd = str(idd)
	#com= db.execute(select([comment.c.comment_text]).where(comment.c.project==result[0] )).fetchone()
	if result[0] is not None:
		print("Adding to DB: Project= "+stridd+" User: "+username+" Text :"+value)
		db.execute(comment.insert(), [ {'project': result[0], 'user': username, 'comment_text': value}])
	return ""

def getCom(title):
	#INIT
	print('Getting com')
	session['username']=request.cookies.get('username')
	db = engine.connect()
	
	#get project id
	result = db.execute(select([project.c.id]).where(project.c.project_name==title)).fetchone()
	print("Searching for project number "+str(result[0])+" comment")
	com=db.execute(select([comment.c.comment_text,comment.c.user]).where(comment.c.project==result[0])).fetchall()
	#j = join(comment,project, comment.c.project == project.c.id)
	#com=db.execute(select([comment.c.comment_text,comment.c.user, comment.c.project]).select_from(j)).fetchall()
	print(len(com))
	#if 
	l=[]
	for i in range(0, len(com)):
		for j in range(0, len(com[i])):
			l.append(com[i][j])
		
	return l

@app.route('/get_printer')
def getAllPrinter():
	#INIT
	print('Getting printer')
	db = engine.connect()
	pr=db.execute(select([printer.c.address, printer.c.user])).fetchall()
	print(type(pr))
	
	return dumps(pr)

# ............................................................................................... #
if __name__ == '__main__':
	app.run(debug=True)
	app.logger.debug("Debug")
# ............................................................................................... #
