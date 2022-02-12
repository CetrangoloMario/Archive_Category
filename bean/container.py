
import re
import databaseManager
from typing import List


class Container:

   def __init__(self, name_container:str =None, name_storage: str =None, list_blob: List=None ):
        self.name_container= name_container
        self.name_storage=name_storage
        self.list_blob= [] if list_blob is None else list_blob
      
   def getNameContainer(self):
      return self.name_container
   
   def getNameStorage(self,):
      return self.name_storage
   
   def getContainerbyStorage(self, name_storage, nomeContainer: str):
      return databaseManager.DatabaseManager.getContainerbyStorage(name_storage, nomeContainer)

      
      
   
      
