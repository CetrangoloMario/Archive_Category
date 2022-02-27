
import re
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
   
   
      
      
   
      
