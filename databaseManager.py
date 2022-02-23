from ast import For
from pickle import TRUE
from queue import Empty
import re
import pyodbc
from bean.blob import Blob
from bean.storage import Storage
from bean.user import User
from bean.container import Container
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
        register = True
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    
                    cursor.execute("INSERT INTO storage VALUES (?,?,?,?)",storage.getStorageName(),storage.getKeyStorage(), storage.getIdUserStorage(), storage.getPwd())
                except pyodbc.IntegrityError:
                    print("integrity error")
                    register=False
                    return register
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
                if len(row)>0:
                    user=User()
                    user.id_user=str(row[0])
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
                #print("riga: ",row)

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

                
        return None


    @staticmethod
    def delete_storage(arc: Storage):
        register = False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("Delete storage Where name=?", arc.getStorageName)
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
        register = True
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO container VALUES (?,?)",container.getNameContainer(),container.getNameStorage())
                except pyodbc.IntegrityError:
                    register=False
                    print("integrity error")
                    return register
                #row = cursor.fetchone() 
        return register
    
    @staticmethod
    def inser_container_multiple(containers : list, name_storage):
        register = True
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                #try:
                    cursor.execute("INSERT INTO container VALUES (?,?) , (?,?) , (?,?) , (?,?) , (?,?), (?,?)",
                    
                        containers[0],name_storage, #container temporaneo
                        containers[1],name_storage, #container businesss
                        containers[2],name_storage, #container enternainemnt
                        containers[3],name_storage, #container politcs
                        containers[4],name_storage, #container sport
                        containers[5],name_storage,  #container tech
                    )
                #except pyodbc.IntegrityError:
                    register=False
                    print("integrity error contanier multiple")
                    return register
                #row = cursor.fetchone() 
        return register
    
    
    @staticmethod
    def insert_blob(blob: Blob):
        register = True
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                   
                    cursor.execute("INSERT INTO blob VALUES (?,?,?,?)", blob.getName(),blob.getNameContainer(),blob.getCrypto(),blob.getCompression())
                except pyodbc.IntegrityError:
                    register=False
                    print("integrity error")
                    return register
                #row = cursor.fetchone() 
                
        return register


    
    
    @staticmethod
    def getListContainerbyStorage(name_storage: str ):
        list=[]
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM container where nome_storage=?",name_storage)
                row = cursor.fetchone()
                
                if len(row)>0:
                    while row:
                        temp=Container()
                        temp.name_container=str(row[0])
                        temp.name_storage=str(row[1])
                        row = cursor.fetchone()
                        list.append(temp)
                    return list
                    
        return None
    
    @staticmethod
    def getContainerbyName(name_storage: str, nomeContainer : str):
        
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM container where nome_storage=? AND name=?",name_storage,nomeContainer)
                row = cursor.fetchone()
                if len(row) > 0:
                    temp=Container()
                    temp.name_container=str(row[0])
                    temp.name_storage=str(row[1])
                    return temp
                else:
                    return None
        
                
    


    @staticmethod
    def getStorageByNome(nome: str):
       
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM storage where name=?",nome)
                row = cursor.fetchone()
                if len(row) > 0:
                    storag=Storage()
                    storag.storage_name=str(row[0])
                    storag.key_storage=str(row[1])
                    storag.id_user=str(row[2])
                    storag.pwd=str(row[3])
                    return storag
        return None
    
    @staticmethod #
    def getBlobByName(nome: str):
        
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM blob where nomeblob=?",nome)
                row = cursor.fetchone()
                temp=Blob()
                print("row: ",row)
                if len(row) > 0:
                    while row:
                        temp=Blob()
                        temp.name=str(row[0])
                        temp.name_container=str(row[1])
                        temp.crypto=str(row[2])
                        temp.compression=str(row[3])
                        row = cursor.fetchone()   
                    return temp         
        return None
    
    @staticmethod #
    def getListBlob(nome_container: str):
        list=[]
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM blob where name_container=?",nome_container)
                row = cursor.fetchone()
            
                if len(row)>0:
                    while row:
                        temp=Blob()
                        temp.name=str(row[0])
                        temp.name_container=str(row[1])
                        temp.crypto=str(row[2])
                        temp.compression=str(row[3])
                        row = cursor.fetchone()
                        list.append(temp)
                    return list

        return None
    
    
    @staticmethod 
    def getContainerByNameStorage(name_storage: str):
        listNomeContainer=[]
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM container where nome_storage=?",name_storage)
                row = cursor.fetchone()
                print("row: ",row)
                if len(row) > 0:
                    while row:
                        listNomeContainer.append(row[0])
                        row = cursor.fetchone()
        print("lista nome contaoner: ",listNomeContainer)  
        return listNomeContainer

    @staticmethod
    def getPassword(name_storage: str):
        
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT password FROM storage where name=?",name_storage)
                row = cursor.fetchone()
                storage = Storage()
                pwd = storage.getPwdDecript(row[0])
                return pwd  #ritorno ls pwd
        return None
    
    @staticmethod
    def getBlobByStorage(name_storage: str ):
        list=[]
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT nomeblob,name_container from blob INNER JOIN container ON blob.name_container = container.name where container.nome_storage = ?",name_storage)
                row = cursor.fetchone()
                if len(row)>0:
                    while row:
                        temp=Blob()
                        temp.name=str(row[0])
                        temp.name_container=str(row[1])
                        row = cursor.fetchone()
                        list.append(temp)
                    return list
                  
        return None


    @staticmethod
    def deleteBlob(nome_blob: str, nome_container ):
        
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("DELETE * from blob where nomeblob=? AND name_container =?",nome_blob,nome_container)
                except pyodbc.IntegrityError:
                    print("Delete error")       
                    return False    
                    
        return True

    

