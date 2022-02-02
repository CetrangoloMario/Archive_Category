from typing_extensions import Self
import archivio
class User:
    def __init__(self, id:str =None,nome:str=None, list_archive: list=() ):
        self.id_user=id
        self.nome_rg=nome
        self.list_archive= list()

    def add_archive(self, archive):
        self.list_archive.append(archive)
        
    def set_nome_rg(self, nome:str=None):
        self.nome_rg=nome

    


        