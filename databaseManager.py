import pyodbc
from bean.archivio import Archivio
import bean.user as User
from bean.resource_group import ResourceGroup
from typing import List

#dati di configurazione per l'utilizzo del database SQL
server = ''
database = ''
username = ''
password = ''   
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
                cursor.execute("SELECT nome FROM ResourceGroup where nome=?",nome)
                row = cursor.fetchone()
                while row:
                    register=True
                    row = cursor.fetchone() 
        return register

    @staticmethod
    def insert_archivio(archivio: Archivio):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO Storage VALUES (?,?)",archivio.getStorageName(),archivio.getKeyStorage())
                #row = cursor.fetchone()
                #while row:
                register=True
                #row = cursor.fetchone() 
        return register

    @staticmethod
    def insert_resource_group(rg: ResourceGroup):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO ResourceGroup VALUES (?)",rg.getNomeResourceGroup())
                register = True
                #row = cursor.fetchone()
                #while row:
                    #register=True
                    #row = cursor.fetchone() 
        return register

    @staticmethod
    def insert_user(user: User):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO Person VALUES (?,?,?,?)",user.getIdUser(),user.getNomeRg(),user.getUserStorageAccount(),user.getUserAccountKey())
                #row = cursor.fetchone()
                #while row:
                register=True
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



    

