from typing import Container
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from databaseManager import DatabaseManager
from bean.user import User
from bean.storage import Storage
from bean.container import Container
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from utilities.crypto import Crypto
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
)
from botbuilder.core import MessageFactory, UserState

from azure.mgmt.resource import ResourceManagementClient

#passi utente carica il file, poi viene categorizzato dal servizio machine learning, (serve blob temporaneo)
#dopo averlo caricato dialogo per inserire alcuni tag da stabilire, compressione cripto e cancellazione del file temporaneo.
#utente carica il file, viene categorizzato se utente accetta la categoria ok se no si deve far scegliere utente tra le categorie gia preseti 
#cioè container già creati standard e dall'utente personali oppure dare la possibilità di creare uno nuovo.

class Upload_file_dialog(ComponentDialog):

    
    def __init__(self, dialog_id: str = None):
        super(Upload_file_dialog,self).__init__(dialog_id or Upload_file_dialog.__name__)   
        self.connection_string = ""
        self.user = User()
        self.add_dialog(
            WaterfallDialog(
                "WFUploadFile", [
                    self.decide_upload, #decidere se carica un file oppure no
                    self.upload,
                    self.step_category,#machine learning
                    """
                    self.step_choice, #scelta utente ok va WFDialogOption
                    self.step_choice_category,#scelta tra categorie esistenti o crea una nuova"""
                    ]
            )
        )

        self.add_dialog(AttachmentPrompt(AttachmentPrompt.__name__,Upload_file_dialog.file_prompt_validator))   #prendere il file in input



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

    
    async def decide_upload(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        await step_context.context.send_activity("....Sei nella sezione carica file... Inizia a caricare un file")
        return await step_context.prompt(
               AttachmentPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("......Inserisci il file da caricare.....")
                ),
            )
    
    async def upload(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        print("sto in upload")
        file = step_context.result[0]  #prelevo il file è un dict

        nome_blob = file.__dict__["name"] #prelevare il nome del file
       
        
        """recupero lo storage account"""
        row = self.user.getStorageAccounteKey(step_context.context.activity.from_property.id) #riga 0 --> storage account , riga 1 account key

        """processo di decifratura"""
        crypto = Crypto()
        cipher = row[1] #prelevo l'account key cifrato
        plaintext = crypto.decrypt(cipher) #decifro
        storage = Storage(row[0],plaintext)  #creo lo storage

        """Connessione allo storage account"""
        STORAGE_ACCOUNT_NAME = storage.getStorageName()
        ACCOUNT_KEY = storage.getKeyStorage()
        self.connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={ACCOUNT_KEY}"
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        container = Container()
        name_container_temp = container.getContainerTempByNameStorage(STORAGE_ACCOUNT_NAME)
    
        blob_client = blob_service_client.get_blob_client(container=name_container_temp, blob=nome_blob) 
        blob_client.upload_blob_from_url(file.__dict__["content_url"]) #prelevo l'url per caricare il file nel blob
        await step_context.context.send_activity("....File caricato con successo nel container temporaneo.....")
        return await step_context.next(1)

    
    async def step_category(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("....Step machine learning.....")


    

    



    
    @staticmethod
    async def file_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            await prompt_context.context.send_activity(
                "....Non hai caricato nessun file..."
            )
            # We can return true from a validator function even if recognized.succeeded is false.
            return True
        
        attachments = prompt_context.recognized.value
        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["text/plain"]
        ]

        prompt_context.recognized.value = valid_images
        return len(valid_images) > 0 







        



        

        


    

