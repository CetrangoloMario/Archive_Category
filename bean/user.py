import re
from bean.storage import Storage
from typing import List


class User:
    def __init__(self, id:str =None,nome_rg:str=None, list_storage: List = None ):
        self.id_user=id
        self.nome_rg=nome_rg
        self.list_storage= [] if list_storage is None else list_storage
    
    def getIdUser(self):
        return self.id_user
    
    def getNomeRg(self):
        return self.nome_rg
   
    def add_storage(self, storage:Storage):
        self.list_storage.append(storage)
    
    def delete_storage(self, storage:Storage):
        self.list_storage.remove(storage)
    
    def get_list_storage(self):
        return self.list_storage

    def set_nome_rg(self, nome:str=None):
        self.nome_rg=nome
    


    


        