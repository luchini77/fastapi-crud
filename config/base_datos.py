import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


fichero = "../datos.sqlite"
#LEEMOS EL DIRECTORIO ACTUAL DE LA BBDD
directorio = os.path.dirname(os.path.realpath(__file__))
#DIRECCION DE LA BBDD
ruta = f"sqlite:///{os.path.join(directorio, fichero)}"
#CREAMOS EL MOTOR
motor = create_engine(ruta, echo=True)
#CREAMOS LA SESSION
sesion = sessionmaker(bind=motor)
#CREAR BASE PARA LAS TABLAS
base = declarative_base()