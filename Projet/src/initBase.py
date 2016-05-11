from sqlalchemy import *
from sqlalchemy.sql import *

engine = create_engine('sqlite:///lama.db', echo = True)   

metadata = MetaData()                                     

usagers = Table('usager', metadata,
            Column('pseudo', String, primary_key = True, unique = True, nullable = False),
			Column('mot_de_passe', String),
			Column('mail', String),
			Column('nom', String),
			Column('prenom', String),
			Column('adresse', String),
			Column('date_de_creation', String),
			Column('score', Integer),
			Column('imprimante', String), #'oui' ou 'non'
			Column('date_de_naissance', String))

projet = Table('projet', metadata,
            Column('id', Integer, autoincrement = True, primary_key = True, nullable = False, unique = True),
			Column('date_de_creation', String),
			Column('usager', String, ForeignKey('usager.pseudo', ondelete = 'SET NULL', onupdate = 'CASCADE')),
			Column('nom_du_projet', String),
			Column('score', Integer),
			Column('type_de_projet', Integer), #'demande', 'publication' ou 'offre'
			Column('description', Integer))

fichier = Table('fichier', metadata,
				Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
				Column('date_de_creation', String),
				Column('score', Integer),
				Column('projet', Integer, ForeignKey('projet.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
				Column('dimensions', String), # exemple: '3cmx4cm'
				Column('poids', Float),
				Column('prix', String), # exemple '€23.4'
				Column('nom', String))
				
commentaire = Table('commentaire', metadata,
				Column('id', Integer, autoincrement=True, primary_key=True, nullable = False, unique = True),
				Column('date_de_creation', String),
				Column('score', Integer),
				Column('projet', Integer, ForeignKey('projet.id', ondelete = 'SET NULL', onupdate = 'CASCADE')),
				Column('usager', String, ForeignKey('usager.pseudo', ondelete = 'SET NULL', onupdate = 'CASCADE')),
				Column('texte_du_commentaire', String))
			


metadata.create_all(engine)                               
connection = engine.connect()                             

#http://docs.sqlalchemy.org/en/latest/core/constraints.html#on-update-and-on-delete
#https://www.sqlite.org/foreignkeys.html
#http://stackoverflow.com/questions/6720050/foreign-key-constraints-when-to-use-on-update-and-on-delete
#file:///C:/Users/Matias/Downloads/03-sqlalchemy-core%20(1).html                                              

connection.close()