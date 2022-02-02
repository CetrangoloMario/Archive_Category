import pyodbc
from bean import User
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
                cursor.execute("SELECT UserId FROM Person where userid=?",iduser)
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
                cursor.execute("SELECT nome FROM Person where nome=?",nome)
                row = cursor.fetchone()
                while row:
                    register=True
                    row = cursor.fetchone() 
        return register  
    

