import re
from typing import List

class Storage:#si aggingono mano mano i tag .... tipo di compressione criptazione scelta.

    def __init__(self, storage_account:str =None, account_key:str = None, id_user:str = None, pwd:str =None, list_container: List = None):
        self.storage_name=storage_account
        self.key_storage=account_key
        self.id_user=id_user
        self.pwd=pwd
        self.listContainer=[] if list_container is None else list_container
    
    def getStorageName(self):
        return self.storage_name
    
    def getKeyStorage(self):
        return self.key_storage

    def getIdUserStorage(self):
        return self.id_user
    
    def getPwd(self):
        return self.pwd



        