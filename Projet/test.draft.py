#TO DELETE IF OTEHR printer_create IS OK
def printer_create(username, xyz, res, price, material, address):
	#engine = create_engine('sqlite:///lama.db', echo=True)
	db = engine.connect()
	try:
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
		pass

# Le template n'existe plus (renommé)
@app.route('/project/<title>')
def viewproject(title):
	db = engine.connect()
		
	if request.method == 'GET':
		return render_template("project.html", name="Projet \"" +title+ "\"", title=title)
	if session.get('logged') is False:
		return redirect('/login')
	return render_template("propose.html")


#TO DELETE IF OTEHR PROPOSE IS OK			
@app.route('/propose', methods=['GET','POST'])
def propose():
	
	username = getUserName(request)
	if username is None:
			print('Pas de cookie')
			return redirect('/login')
	elif username is not None:

		if request.method == 'GET':
				return render_template("propose.html", name = "Proposition de projet")
		
		if request.method == 'POST':
			db = engine.connect()
			result = db.execute(select([file.c.project]).where(file.c.name==username)).fetchone()
			#if result is None:
			#db.execute(project.insert(), [ {'project_name': request.form['title'], 'user':session['username']}])
			print('create project')
			return redirect('/project/'+request.form['title'])
			#else:
			#	print('Vous avez déjà créé ce projet')
			return redirect('/')


#TO DELETE IF OTEHR RENT IS OK	
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
