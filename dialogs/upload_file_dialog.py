from typing import Container
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from databaseManager import DatabaseManager
from bean.user import User
from bean.storage import Storage
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

#passi utente carica il file, poi viene categorizzato dal servizio machine learning, (serve blob temporaneo)
#dopo averlo caricato dialogo per inserire alcuni tag da stabilire, compressione cripto e cancellazione del file temporaneo.
#utente carica il file, viene categorizzato se utente accetta la categoria ok se no si deve far scegliere utente tra le categorie gia preseti 
#cioè container già creati standard e dall'utente personali oppure dare la possibilità di creare uno nuovo.

class Upload_file_dialog(CancelAndHelpDialog):

    
    def __init__(self, dialog_id: str = None):
        super(Upload_file_dialog,self).__init__(dialog_id or Upload_file_dialog.__name__)   
        self.connection_string = ""
        self.user = User()
        self.add_dialog(
            WaterfallDialog(
                "WFUploadFile", [
                    self.upload,#in che storageaccount vuoi inserirlo prima domanda
                    """
                    self.step_category,#machine learning
                    self.step_choice, #scelta utente ok va WFDialogOption
                    self.step_choice_category,#scelta tra categorie esistenti o crea una nuova"""
                    ]
            )
        )
        """
        self.add_dialog(
            WaterfallDialog(
                "WFDialogOption", [
                    self.step_traduction,
                    self.step_compression,
                    self.step_crypto,
                    self.step_final  #salva nel container scelto e cancella quelli temporanei.
                    ]
            )
        )
        """

        self.initial_dialog_id = "WFUploadFile"

    
    async def upload(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #recuperare storage account e account key
        row = self.user.getStorageAccounteKey(step_context.context.activity.from_property.id)
        await step_context.context.send_activity("Controlliamo se hai già un contenitore!!!!")
        #print("riga del database: ",row)
        storage = Storage(row[0],row[1])  #riga 0 --> storage account , riga 1 account key
        STORAGE_ACCOUNT_NAME = storage.getStorageName()
        ACCOUNT_KEY = storage.getKeyStorage()
        self.connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={ACCOUNT_KEY}"
        #print("stringa di connessione: ",self.connection_string)
        # Create the BlobServiceClient object which will be used to create a container client
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        list_response = blob_service_client.list_containers()
        


    

