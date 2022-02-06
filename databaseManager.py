from ast import For
import pyodbc
from bean.storage import Storage
from bean import user as User
from bean.user import User 
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
                cursor.execute("SELECT userid FROM User where userid=?",iduser)
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
                cursor.execute("SELECT nomeRG FROM User where nomeRG=?",nome)
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
                    cursor.execute("INSERT INTO Storage VALUES (?,?,?,?)",Storage.getStorageName(),Storage.getKeyStorage(), Storage.getIdUserStorage(), Storage.getPwd())
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
                    cursor.execute("INSERT INTO User VALUES (?,?)",user.getIdUser(),user.getNomeRg())
                    
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
                cursor.execute("SELECT nome, key FROM Storage where userid=?",iduser)
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
                    cursor.execute("Delete INTO Storage Where accountStorage=?", arc.getStorageName)
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
                    cursor.execute("Delete INTO Storage Where iduser=?", iduser)
                    register=True
                except Exception:
                    register=False

                #row = cursor.fetchone() 
        return register

    

