import re
import databaseManager

class User:
    def __init__(self, id:str =None,nome:str=None,userStorageAccount: str=None,userAccountKey: str=None,list_archive: list=()):
        self.id_user=id
        self.nome_rg=nome
        self.user_storage_account = userStorageAccount
        self.user_account_key = userAccountKey
        self.list_archive= list()
    
    def getIdUser(self):
        return self.id_user
    
    def getNomeRg(self):
        return self.nome_rg
    
    def getUserStorageAccount(self):
        return self.user_storage_account
    
    def getUserAccountKey(self):
        return self.user_account_key


    def add_archive(self, archive):
        self.list_archive.append(archive)
        
    def set_nome_rg(self, nome:str=None):
        self.nome_rg=nome
    
    #otteine il storage account e account key
    def getStorageAccounteKey(self,iduser: str):
        return databaseManager.DatabaseManager.get_storage_account(iduser)

    


        