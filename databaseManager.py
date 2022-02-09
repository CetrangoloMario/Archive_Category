from ast import For
import pyodbc
from bean.container import Container
from bean.storage import Storage
from bean import user as User
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

    #ottiene storage account e account key una tupla () , altrimenti restituisce None
    @staticmethod
    def get_storage_account(iduser: str):
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name, keystorage FROM storage where iduser=?",iduser)
                row = cursor.fetchone()
                if len(row) > 0:
                    return row
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
    
    def getContainerTempByNameStorage(name_storage: str):
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM container where nome_storage=? AND name LIKE('%temp%');",name_storage)
                row = cursor.fetchone()
                if len(row) > 0:
                    return row[0]  #restituisco solo il nome del container temporaneo
        return None




    

