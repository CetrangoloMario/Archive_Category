from typing import Container
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from databaseManager import DatabaseManager
from bean.user import User
from bean.archivio import Archivio
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__


class CaricaFileDialog(CancelAndHelpDialog):
    
    def __init__(self, dialog_id: str = None):
        super(CaricaFileDialog,self).__init__(dialog_id or CaricaFileDialog.__name__)   
        self.connection_string = ""
        self.user = User()
        self.add_dialog(
            WaterfallDialog(
                "CaricaFileDialog", [
                    self.select_first,
                    #self.select_second
                    ]
            )
        )
        self.initial_dialog_id = "CaricaFileDialog"

    
    async def select_first(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #recuperare storage account e account key
        row = self.user.getStorageAccounteKey(step_context.context.activity.from_property.id)
        await step_context.context.send_activity("Controlliamo se hai già un contenitore!!!!")
        print("riga del database: ",row)
        archivio = Archivio(row[0],row[1])  #riga 0 --> storage account , riga 1 account key
        STORAGE_ACCOUNT_NAME = archivio.getStorageName()
        ACCOUNT_KEY = archivio.getKeyStorage()
        self.connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={ACCOUNT_KEY}"
        #print("stringa di connessione: ",self.connection_string)
        # Create the BlobServiceClient object which will be used to create a container client
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        list_response = blob_service_client.list_containers()
        


    

