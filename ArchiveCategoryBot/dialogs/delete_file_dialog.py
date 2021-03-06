from typing import List

from grapheme import length
from bean import *
from bean import container
import databaseManager
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from databaseManager import DatabaseManager
from bean.user import User
from bean.storage import Storage
from bean.container import Container
from bean.blob import Blob
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

from datetime import datetime, timedelta
from azure.storage.blob import BlobClient, generate_blob_sas, BlobSasPermissions

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

from azure.mgmt.resource import ResourceManagementClient
from config import DefaultConfig

CONFIG = DefaultConfig
#main_dialog=MainDialog(CONFIG.CONNECTION_NAME,)

"""passi sono utente digita il nome o deve selezionare storage acount, da li può selezionare un container e visualizza tutti i file, o seleziona il file o deve toranere alla visualizza container, che gli potrebbe permettere visualizza storage
 MC: capitò io volevo sapere se quando faccio scorrere fllusso ivece di fa spep.contest.next posso fare step begin (WFdialogView. funzionedello step)
 MC: quindi in sessione mi devosalvare ste cose se no ogni volta devo fa la queryt""" 
class Delete_file_dialog(ComponentDialog):

    
    def __init__(self, dialog_id: str = None):
        super(Delete_file_dialog,self).__init__(dialog_id or Delete_file_dialog.__name__)   
        self.connection_string = ""
        self.user = User()
        self.storage=Storage()
        self.container= Container()
        self.blob= Blob()
        
        #self._main_dialog = main_dialog.id
        
        self.add_dialog(                # allora problema io inserisco nome file o seleziono la ricerca/ se ricerca devo fare dallo storage fino ad arrivare al fileù
            WaterfallDialog(                # se file faccio spep_file che mi da tutti i file con quel nome ma sappiamo che con i vincoli solo un file sarà
                "WFDeleteFile", [         #voglio utilizzare spep file per dopo lo step per la ricerca
                    self.step_initial, # chiedo all'utente nome file o se lo vuole cercare
                    self.option_step,
                    self.step_insert_name_file,
                    self.step_delete
                    #Step successivo dipende dalla scelta se cancellare il file, scaricarlos

                    ]
            )
        )
        
        #dialogo per la ricerca del file
        self.add_dialog(
            WaterfallDialog(
                "WFSearchFile",[
                    self.step_select_storage,
                    self.step_select_container,
                    self.step_select_file,
                    self.step_continue,
                    self.step_delete
                ]
            )
        )
        
        self.initial_dialog_id="WFDeleteFile"

    async def step_initial(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        await step_context.context.send_activity("....Sei nella sezione cancella file....")
        card = HeroCard(
        text ="Scegli il file da cancellare, tramite il nome o cerando all'interno dell'archivio",
            buttons = [
                CardAction(
                    type=ActionTypes.im_back,
                    title ="Nome File",
                    value="nome_file"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title ="Ricerca ALL",
                    value="all"
                )
            ]
            )
        return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    MessageFactory.attachment(CardFactory.hero_card(card))
                ),
            )
                
    async def option_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result=="reprompt-main":
            await step_context.context.send_activity("Ritorniamo al main")
            #step_context.values["skip"]=
            return await step_context.end_dialog()#testare
        
        option=step_context.result
        
        if option=="nome_file": ## Riassunto account dimensione storage ....
            await step_context.context.send_activity("hai scelto Ricerca per nome")
            return await step_context.next([])

        if option=="all":
            await step_context.context.send_activity("hai scelto ricerca all'interno dell'Archivio")
            return await step_context.begin_dialog("WFSearchFile")#testare

       
        
    async def step_insert_name_file(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result=="reprompt-main":
            await step_context.context.send_activity("Ritorniamo al main")
            #step_context.values["skip"]=
            return await step_context.end_dialog()#testare
        
        message_text = "Inserisci nome file: \n"
        prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
        return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        
        
        #step download
    async def step_delete(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        
        nomeFile= step_context.result#sia caso ricerca che inserito nome
        
        
        blob=DatabaseManager.getBlobByName(nomeFile)#return lista (lista per il momento contiene solamente un file con i vincoli del db) o None
        
        #print("blob: ",blob)

        if blob is None:
            await step_context.context.send_activity(" File non trovato ")
            return await step_context.end_dialog("reprompt-main")
        
        else:
            await step_context.context.send_activity(" File trovato un solo elemento")
            self.name_container=blob.getNameContainer()#cosi il container
            listaStorageUser=DatabaseManager.getListStorageByID(step_context.context.activity.from_property.id)
            if listaStorageUser is not None:
                storage=Storage()
                storage=listaStorageUser[0]
                await step_context.context.send_activity("File cancellato: ")
                #cancellare nel db
                if self.delete_file(blob.getName(),storage,self.name_container):
                    DatabaseManager.deleteBlob(blob.getName(),self.name_container)
                    return await step_context.end_dialog("reprompt-main")
                await step_context.context.send_activity(" File errore eliminazione")
                return await step_context.end_dialog("reprompt-main")
                
            
            await step_context.context.send_activity(" Archivio corrente non trovato ")
            return await step_context.end_dialog("reprompt-main")
            
      
    
    async def step_select_storage(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        
        iduser=step_context.context.activity.from_property.id

        user= DatabaseManager.get_user(iduser)
        if user is None:
            return await step_context.cancel_all_dialogs()
        nome_RG=user.getNomeRg()
        #print (RG,"")
        
        """recupero lista storage account"""
        list=DatabaseManager.getListStorageByID(iduser)
        #Devo far selezionare storage account nuovo step
        listselect=[]
        #print(list,"lista")

    
        for x in list:
            object=CardAction(
                type=ActionTypes.im_back,
                title =x.getStorageName(),
                value=x.getStorageName()
            )
            listselect.append(object)
            
        listselect.append(CardAction(
                type=ActionTypes.im_back,
                title ="Torna indietro",
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
        
        
    
    async def step_select_container(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option=step_context.result
        
        if option=="logout": 
            await step_context.context.send_activity("Torna al menù principale")
            return await step_context.end_dialog("reprompt-main")
        
        iduser=step_context.context.activity.from_property.id
        list=DatabaseManager.getListStorageByID(iduser)
        archivio=DatabaseManager.get_user(iduser).getNomeRg()
        step_context.values["nome_archivio"]  = archivio
        lista_container=DatabaseManager.getListContainerbyStorage(option)
        
        if lista_container is None:
            await step_context.context.send_activity("Torna al menù principale non trovata lista contenitori")
            return await step_context.end_dialog("reprompt-main")
        listselect=[]
        
        for x in lista_container:
            
            if x.getNameContainer() == archivio+CONFIG.CONTAINER_BLOB_TEMP:
                    break
            object=CardAction(
                type=ActionTypes.im_back,
                title =x.getNameContainer(),
                value=x.getNameContainer()
            )
            listselect.append(object)
            
        listselect.append(CardAction(
                type=ActionTypes.im_back,
                title ="Torna indietro",
                value="logout"
            ))
        
        card = HeroCard(
        text ="Ciao,seleziona il container. Per uscire digita quit o esci.",
        buttons = listselect)
        
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )
        
        
    
    async def step_select_file(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option=step_context.result
        
        if option=="logout": 
            await step_context.context.send_activity("Torna al menù principale")
            return await step_context.end_dialog("reprompt-main")
        
        iduser=step_context.context.activity.from_property.id
        lista_file=DatabaseManager.getListBlob(option)
        if lista_file is None:
            await step_context.context.send_activity("Torna al menù principale non sono presenti file")
            return await step_context.end_dialog("reprompt-main")
        listselect=[]
        
        for x in lista_file:
            object=CardAction(
                type=ActionTypes.im_back,
                title =x.getName(),
                value=x.getName()
            )
            listselect.append(object)
            
        listselect.append(CardAction(
                type=ActionTypes.im_back,
                title ="Torna indietro",
                value="logout"
            ))
        
        card = HeroCard(
        text ="Ciao,seleziona il file. Per uscire digita quit o esci.",
        buttons = listselect)
        
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )
        
    async def step_continue(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option=step_context.result
        
        if option=="logout": 
            await step_context.context.send_activity("Torna al menù principale")
            return await step_context.end_dialog("reprompt-main")
        
        else:
            return await step_context.next(option)
        
        
    
    #Cancella file, cancella db
    @staticmethod       
    def delete_file(nome_blob: str, storage: Storage, nome_container: str):
        
        #oggetto blob_client ho come variabile di istanza, nome container e nome storage in istanza.
        
        NAMESTORAGE=storage.getStorageName()
        
        #key 
        ACCOUNT_KEY = storage.getKeyStorageDecript(storage.getKeyStorage())
        #try:
        connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={NAMESTORAGE};AccountKey={ACCOUNT_KEY}"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client= blob_service_client.get_blob_client(container= nome_container, blob=nome_blob )
        blob_client.delete_blob()
        
        return  True
            
        
        
    