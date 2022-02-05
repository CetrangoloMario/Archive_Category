import pyodbc
from bean.storage import Storage
from bean import user as User
from bean.user import User 
from typing import List
from config import DefaultConfig

CONFIG = DefaultConfig

#dati di configurazione per l'utilizzo del database SQL
server = CONFIG.serverdb
database = CONFIG.databasedb
username = CONFIG.usernamedb
password = CONFIG.passworddb
driver= '{ODBC Driver 17 for SQL Server}'


class DatabaseManager:

    @staticmethod
    def user_is_registered(iduser: str):
        register=False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT userid FROM Person where userid=?",iduser)
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
                cursor.execute("SELECT nomeRG FROM Person where nomeRG=?",nome)
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
                cursor.execute("INSERT INTO Storage VALUES (?,?)",Storage.getStorageName(),Storage.getKeyStorage())
                #row = cursor.fetchone()
                #while row:
                register=True
                #row = cursor.fetchone() 
        return register

    

    @staticmethod
    def insert_user(user: User):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO Person VALUES (?,?,?,?)",user.getIdUser(),user.getNomeRg(),user.getUserStorageAccount(),user.getUserAccountKey())
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
                cursor.execute("SELECT userAccountStorage, userAccountKey FROM Person where userid=?",iduser)
                row = cursor.fetchone()
                if len(row) > 0:
                    return row
        return None


    @staticmethod
    def delete_archive(arc: Storage):
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

    

