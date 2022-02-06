import re
from xmlrpc.client import Boolean
from bean.storage import Storage
import databaseManager
from typing import List

class Blob:
    def __init__(self, name:str =None,name_container:str=None, crypto: str=None, compression: str=None ):
        self.name=name
        self.name_container=name_container
        self.crypto=crypto
        self.compression=compression


        