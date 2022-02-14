
from typing import List
from unicodedata import name
from aiohttp import request

from grapheme import length
import databaseManager
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from databaseManager import DatabaseManager
from bean.user import User
from bean.storage import Storage
from bean.container import Container
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from utilities.crypto import Crypto
from botbuilder.core import BotFrameworkAdapter
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.core import MessageFactory, TurnContext, CardFactory, UserState
from botbuilder.schema import Attachment, InputHints, SuggestedActions
from botbuilder.dialogs.choices import Choice
from botbuilder.schema import (
    ChannelAccount,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes,
)

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
import http.client, urllib.request, urllib.parse, urllib.error, base64
import requests 

from utilities.classificatordocument import ClassificatorDocument
from azure.mgmt.resource import ResourceManagementClient
from config import DefaultConfig

CONFIG = DefaultConfig

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
                    self.step_select_storage,
                    self.step_initial, 
                    self.upload,
                    self.step_category,#machine learning
                   
                    
                    #self.step_choice_category,#scelta tra categorie esistenti o crea una nuova"""
                    #self.step_choice, #scelta utente ok va WFDialogOption
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

        self.step_select_storage = "WFUploadFile"

    
    async def step_select_storage(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        await step_context.context.send_activity("....Sei nella sezione carica file... Inizia a caricare un file")
        await step_context.context.send_activity("\n...Seleziona lo storage dove vuoi caricarlo...")
       
        iduser=step_context.context.activity.from_property.id

        user= DatabaseManager.get_user(iduser)
        RG=user.getNomeRg()
        print (RG,"")
        
        """recupero lista storage account"""
        list=DatabaseManager.getListStorageByID(iduser)
        #Devo far selezionare storage account nuovo step
        listselect=[]
        print(list,"lista")



        for x in list:
            object=CardAction(
                type=ActionTypes.im_back,
                title =x.getStorageName(),
                value=x.getStorageName()
            )
            listselect.append(object)
            
        listselect.append(CardAction(
                type=ActionTypes.im_back,
                title ="Logout",
                value="logout"
            ))
        
        card = HeroCard(
        text ="Ciao,seleziona lo storage. Per uscire digita quit o esci.",
        buttons = listselect)
        
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )
        
        
    
    async def step_initial(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option=step_context.result

        if option=="logout": 
            bot_adapter: BotFrameworkAdapter = step_context.context.adapter
            await bot_adapter.sign_out_user(step_context.context, self.connection_name)
            await step_context.context.send_activity("Sei stato disconnesso.")
            return await step_context.cancel_all_dialogs()
            
        else:
            step_context.values["select_storage"] = option
            
        return await step_context.prompt(
               AttachmentPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("......Inserisci il file da caricare.....oppure digita un messaggio per tornare indietro")
                ),
            )
        
     
       
            
    
    
    
    async def upload(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        print("sto in upload")
        file = step_context.result[0]  #prelevo il file è un dict

        nome_blob = file.__dict__["name"] #prelevare il nome del file
        print("Nome blob: ",nome_blob)
        step_context.values["name-blob"] = nome_blob #salvo in sessione

        iduser=step_context.context.activity.from_property.id
        RG = databaseManager.DatabaseManager.get_user(iduser)
        NAMESTORAGE=step_context.values["select_storage"]
        
        #key
        storagetemp = DatabaseManager.getStorageByNome(NAMESTORAGE)
        
        ACCOUNT_KEY = storagetemp.getKeyStorageDecript(storagetemp.getKeyStorage())

        self.connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={NAMESTORAGE};AccountKey={ACCOUNT_KEY}"
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        #modificare (id , storage accout selezionato) lista container
        name_container_temp= DatabaseManager.getContainerbyName(NAMESTORAGE,RG.getNomeRg()+CONFIG.CONTAINER_BLOB_TEMP)
        step_context.values["name-container"] = name_container_temp.getNameContainer()
        try:
            blob_client = self.blob_service_client.get_blob_client(container=name_container_temp.getNameContainer(), blob=nome_blob) 
        except AttributeError:
            await step_context.context.send_activity("....File duplicato....")
            return await step_context.reprompt_dialog()
        print("url: ",file.__dict__["content_url"])
        blob_client.upload_blob_from_url(file.__dict__["content_url"]) #prelevo l'url per caricare il file nel blob
        #inserimento del file nel database
        print("inserito nel blob")

        await step_context.context.send_activity("....File caricato con successo nel container temporaneo.....")

        return await step_context.next(1)



    
    async def step_category(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("....Categorizziamo il file appena caricato.....")
        container = step_context.values["name-container"]
        blob = step_context.values["name-blob"]
        print("container: ",container)
        print("blob: ",blob)
        blob_client = self.blob_service_client.get_blob_client(container=container,blob=blob) #prelevo il blob appena caricato
        with open("./utilities/BlockDestination.txt", "wb") as my_blob:
                download_stream = blob_client.download_blob()
                my_blob.write(download_stream.readall())
        #myblob deve essere passato al machine learnig
        classificator = ClassificatorDocument()
        classificator.classificatorcategory(my_blob)
        
        

        


    @staticmethod
    async def file_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            await prompt_context.context.send_activity(
                "....Non hai caricato nessun file..."
            )
            #dovrebbe tornare al main dialog principale in caso in cui l'utente non vuole piu inserire il file
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







        



        

        


    

