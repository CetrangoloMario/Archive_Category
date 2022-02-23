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
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__,ContentSettings

from datetime import datetime, timedelta
from azure.storage.blob import BlobClient, generate_blob_sas, BlobSasPermissions

from utilities.crypto import Crypto
from botbuilder.core import BotFrameworkAdapter
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.core import MessageFactory, TurnContext, CardFactory, UserState
from botbuilder.schema import Attachment, InputHints, SuggestedActions
from botbuilder.dialogs.choices import Choice

from azure.storage.blob import ResourceTypes, generate_blob_sas,BlobSasPermissions
from utilities.crypt_decrypt import Crypt_decrypt
from datetime import datetime, timedelta

    
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
import requests

CONFIG = DefaultConfig
#main_dialog=MainDialog(CONFIG.CONNECTION_NAME,)

"""passi sono utente digita il nome o deve selezionare storage acount, da li può selezionare un container e visualizza tutti i file, o seleziona il file o deve toranere alla visualizza container, che gli potrebbe permettere visualizza storage
 MC: capitò io volevo sapere se quando faccio scorrere fllusso ivece di fa spep.contest.next posso fare step begin (WFdialogView. funzionedello step)
 MC: quindi in sessione mi devosalvare ste cose se no ogni volta devo fa la queryt""" 
class Download_file_dialog(ComponentDialog):

    
    def __init__(self, dialog_id: str = None):
        super(Download_file_dialog,self).__init__(dialog_id or Download_file_dialog.__name__)   
        self.connection_string = ""
        self.user = User()
        self.storage=Storage()
        self.container= Container()
        self.blob= Blob()
        
        #self._main_dialog = main_dialog.id
        
        self.add_dialog(                # allora problema io inserisco nome file o seleziono la ricerca/ se ricerca devo fare dallo storage fino ad arrivare al fileù
            WaterfallDialog(                # se file faccio spep_file che mi da tutti i file con quel nome ma sappiamo che con i vincoli solo un file sarà
                "WFDownloadFile", [         #voglio utilizzare spep file per dopo lo step per la ricerca
                    self.step_initial, # chiedo all'utente nome file o se lo vuole cercare
                    self.option_step,
                    self.step_insert_name_file,
                    self.step_download
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
                    self.step_download
                ]
            )
        )
        
        self.initial_dialog_id="WFDownloadFile"

    async def step_initial(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        await step_context.context.send_activity("....Sei nella sezione Scarica file... Inizia ad inserire il nome di un file")
        card = HeroCard(
        text ="Scegli se ricercare per nome o cercare manualmente all'interno dell'archivio",
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
        option=step_context.result
        
        if option=="nome_file": ## Riassunto account dimensione storage ....
            await step_context.context.send_activity("hai scelto Ricerca per nome")
            return await step_context.next([])

        if option=="all":
            await step_context.context.send_activity("hai scelto ricerca all'interno dell'Archivio")
            return await step_context.begin_dialog("WFSearchFile")#testare

       
        
    async def step_insert_name_file(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        message_text = "Inserisci nome file: \n"
        prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
        return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        
        
        
        #step download
    async def step_download(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        
        nomeFile= step_context.result#sia caso ricerca che inserito nome
        
        
        blob=DatabaseManager.getBlobByName(nomeFile)#return lista (lista per il momento contiene solamente un file con i vincoli del db) o None
        
        print("blob: ",blob)

        if blob is None:
            await step_context.context.send_activity(" File non trovato ")
            return await step_context.reprompt_dialog()
        
        else:
            await step_context.context.send_activity(" File trovato un solo elemento")
            self.name_container=blob.getNameContainer()#cosi il container
            listaStorageUser=DatabaseManager.getListStorageByID(step_context.context.activity.from_property.id)
            if listaStorageUser is not None:
                storage=Storage()
                storage=listaStorageUser[0]
                await step_context.context.send_activity(MessageFactory.attachment( self.download_file(nomeFile, storage,self.name_container)))
                return await step_context.end_dialog()
            
            await step_context.context.send_activity(" Archivio corrente non trovato ")
            return await step_context.end_dialog()
            
            #return await step_context.begin_dialog(self._main_dialog.begin_dialog("WFDialog"))
        
        #più storage account 
        """
        # Step successivo quando si estende al possesso di più storage account e poi alla condivisione dei file 
        step_context.values["listFile"]=listFile
        
        await step_context.context.send_activity("Trovata una lista di file che matchano....")
        listselect=[]
        for x in listFile:
            object=CardAction(
                type=ActionTypes.im_back,
                title =x.getNameContainer+" > "+x.getName(),
                value=x.getContainer()
            )
            listselect.append(object)
        
        listselect.append(CardAction(
                type=ActionTypes.im_back,
                title ="Scarica Tutti i File",
                value="all_download"
            ))
        
        listselect.append(CardAction(
                type=ActionTypes.im_back,
                title ="Logout",
                value="logout"
            ))
        
        card = HeroCard(
        text ="Ciao,...seleziona la Categoria giusta . Per uscire digita quit o esci.",
        buttons = listselect)
        
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )"""
            
        
        
    
    async def step_select_storage(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        
        iduser=step_context.context.activity.from_property.id

        user= DatabaseManager.get_user(iduser)
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
            bot_adapter: BotFrameworkAdapter = step_context.context.adapter
            await bot_adapter.sign_out_user(step_context.context, self.connection_name)
            await step_context.context.send_activity("Torna al menù principale")
            return await step_context.end_dialog()
        
        iduser=step_context.context.activity.from_property.id
        lista_container=DatabaseManager.getListContainerbyStorage(option)
        listselect=[]
        
        for x in lista_container:
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
        text ="Ciao,seleziona lo storage. Per uscire digita quit o esci.",
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
            bot_adapter: BotFrameworkAdapter = step_context.context.adapter
            await bot_adapter.sign_out_user(step_context.context, self.connection_name)
            await step_context.context.send_activity("Torna al menù principale")
            return await step_context.reprompt_dialog()
        
        iduser=step_context.context.activity.from_property.id
        lista_file=DatabaseManager.get(option)
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
        text ="Ciao,seleziona lo storage. Per uscire digita quit o esci.",
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
            bot_adapter: BotFrameworkAdapter = step_context.context.adapter
            await bot_adapter.sign_out_user(step_context.context, self.connection_name)
            await step_context.context.send_activity("Torna al menù principale")
            return await step_context.reprompt_dialog()
        
        else:
           return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=option)
            )
        
        
    
    
    @staticmethod       
    def download_file(nome_blob: str, storage: Storage(), nome_container: str):
        
        #oggetto blob_client ho come variabile di istanza, nome container e nome storage in istanza.
        
        NAMESTORAGE=storage.getStorageName()
        
        #key 
        ACCOUNT_KEY = storage.getKeyStorageDecript(storage.getKeyStorage())
        #try:
        connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={NAMESTORAGE};AccountKey={ACCOUNT_KEY}"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client= blob_service_client.get_blob_client(container= nome_container, blob=nome_blob )
        type = blob_client.get_blob_properties().get("content_settings")["content_type"]
        
        sas_blob = generate_blob_sas(account_name=blob_client.account_name, 
                            container_name=nome_container,
                            blob_name=nome_blob,
                            account_key=ACCOUNT_KEY,
                            permission=BlobSasPermissions(read=True),
                            expiry=datetime.utcnow() + timedelta(hours=1))
    



      
        

        """creo la key per decifrare"""
        pwd = DatabaseManager.getPassword(NAMESTORAGE)
        key = Crypt_decrypt.make_password(pwd.encode(),b'10')


        """processo di decifratura file"""
        url = 'https://'+blob_client.account_name+'.blob.core.windows.net/'+nome_container+'/'+nome_blob+'?'+sas_blob
        #se dal url me lo leggo nel bot
        #property=blob_client.get_blob_properties()#così
        #dal blob online con le stringhe di proprietà del blob
        response = requests.get(url)
        text = response.content
        plaintext = Crypt_decrypt.decrypt(text,key)

        """creo un blob temporaneo per la decifratura"""
        blob_plain_text = blob_service_client.get_blob_client(container=nome_container+CONFIG.CONTAINER_BLOB_TEMP,blob=nome_blob)
        #blob_plain_text.upload_blob(plaintext,content_settings=ContentSettings(content_type=type),blob_type="BlockBlob")
        #come scarico il testo tradotto dovrei creare un blob o posso creare un file e facc attacchment
        
        return  Attachment(name=nome_blob, content_type=type, content=blob_plain_text)#content_url=url, ) 

           

            #attachment download
        #except Exception():
            #return Exception()
            
        
        
    