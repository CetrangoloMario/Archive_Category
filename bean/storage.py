
class Storage:#si aggingono mano mano i tag .... tipo di compressione criptazione scelta.

    def __init__(self, storage_account:str =None, account_key:str = None):
        self.storage_name=storage_account
        self.key_storage=account_key
    
    def getStorageName(self):
        return self.storage_name
    
    def getKeyStorage(self):
        return self.key_storage


    



    
        