from ast import For
from queue import Empty
import re
import pyodbc
from bean.storage import Storage
from bean.user import User
import bean.container as Container
from bean.blob import Blob
from typing import List
from config import DefaultConfig

CONFIG = DefaultConfig

#dati di configurazione per l'utilizzo del database SQL
server = CONFIG.SERVERDB
database = CONFIG.DATABASEDB
username = CONFIG.USERNAMEDB
password = CONFIG.PASSWORDDB
driver= CONFIG.DRIVERDB


class DatabaseManager:

    @staticmethod
    def user_is_registered(iduser: str):
        register=False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT idUser FROM utente where idUser=?",iduser)
                row = cursor.fetchone()
                while row:
                    register=True
                    row = cursor.fetchone() 
        return register  


    @staticmethod
    def aviability_rg(nome: str):
        register=False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT nomeRG FROM utente where nomeRG=?",nome)
                row = cursor.fetchone()
                while row:
                    register=True
                    row = cursor.fetchone() 
        return register


    @staticmethod
    def insert_storage(storage: Storage):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:

                try:
                    cursor.execute("INSERT INTO storage VALUES (?,?,?,?)",storage.getStorageName(),storage.getKeyStorage(), storage.getIdUserStorage(), storage.getPwd())
                except pyodbc.IntegrityError:
                        pass
                register=True
                #row = cursor.fetchone() 
        return register

    

    @staticmethod
    def insert_user(user: User):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO utente VALUES (?,?)",user.getIdUser(),user.getNomeRg())
                    
                    register=True
                except Exception:
                    register=False

                #row = cursor.fetchone() 
        return register

    @staticmethod
    def get_user(id: str):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM utente WHERE idUser=?",id)
                row = cursor.fetchone()
                if len(row) is not None:
                    user=User()
                    user.id_user=str (row[0])
                    user.nome_rg=str(row[1])
                    user.list_storage=None
                    return user
        return None
    
    #tupla list storage , altrimenti restituisce None
    @staticmethod
    def getListStorageByID(iduser: str):
        list=[]
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM storage where iduser=?",iduser)
                row = cursor.fetchone()
                print("riga: ",row)

                if len(row)>0:
                    while row:
                        storag=Storage()
                        
                        storag.storage_name=str(row[0])
                        storag.key_storage=str(row[1])
                        storag.id_user=str(row[2])
                        storag.pwd=str(row[3])
                        row=cursor.fetchone()
                        list.append(storag)
                    return list

                
                return list
        return None


    @staticmethod
    def delete_storage(arc: Storage):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("Delete INTO storage Where name=?", arc.getStorageName)
                    register=True
                except Exception:
                    register=False

                #row = cursor.fetchone() 
        return register

    @staticmethod
    def delete_total_storage(iduser: str):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("Delete INTO storage Where iduser=?", iduser)
                    register=True
                except Exception:
                    register=False

                #row = cursor.fetchone() 
        return register
    
    @staticmethod
    def insert_container(container: Container):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO container VALUES (?,?)",container.getNameContainer(),container.getNameStorage())
                except pyodbc.IntegrityError:
                        pass
                register=True
                #row = cursor.fetchone() 
        return register
    
    
    @staticmethod
    def getListContainerbyStorage(name_storage: str ):
        list=[]
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM container where nome_storage=?",name_storage)
                row = cursor.fetchone()
                if len(row) > 0:
                    for x in row:
                        list.append(Container(x[0],x[1]))
                return list 
        return None
    
    @staticmethod
    def getContainerbyName(name_storage: str, nomeContainer : str):
        
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM container where nome_storage=? AND name=?",name_storage,nomeContainer)
                row = cursor.fetchone()
                if len(row) > 0:
                    return Container(row[0],row[1]) 
        return None


    @staticmethod
    def getStorageByNome(nome: str):
       
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM storage where name=?",nome)
                row = cursor.fetchone()
                if len(row) > 0:
                    return Storage(row[0],row[1],row[2],row[3])
        return None



    

