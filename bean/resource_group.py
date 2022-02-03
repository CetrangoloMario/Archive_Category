

class ResourceGroup:

    def __init__(self, nome_resource:str = None):
         self._nome_resource = nome_resource
    
    def getNomeResourceGroup(self):
        return self._nome_resource

