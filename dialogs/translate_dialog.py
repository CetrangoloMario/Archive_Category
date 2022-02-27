from multiprocessing.connection import wait
from unicodedata import name
from botbuilder.dialogs import ComponentDialog, DialogTurnResult, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from bean.blob import Blob
from databaseManager import DatabaseManager
from azure.storage.blob import BlobServiceClient, BlobClient, __version__,ContentSettings, generate_blob_sas,BlobSasPermissions,generate_container_sas
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, CardFactory
from botbuilder.schema import (
    HeroCard,
    CardAction,
    ActionTypes,
    Attachment,
)
from utilities.crypt_decrypt import Crypt_decrypt

import uuid, json

from botbuilder.dialogs.prompts import (
    TextPrompt,
    PromptOptions, 
)
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient,DocumentTranslationInput,TranslationTarget
from config import DefaultConfig
import requests
import datetime
from azure.core.exceptions import ResourceExistsError


CONFIG = DefaultConfig()

class Translate_Dialog(ComponentDialog):

    def __init__(self, dialog_id: str = None):
        super(Translate_Dialog,self).__init__(dialog_id or Translate_Dialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                "WFDialogTranslate", [
                    self.step_select_storage, #sceglie lo storage
                    self.select_file, #sceglie il file da tradurre
                    self.step_lingua, 
                    self.step_translate,  #step traduzione
                    ]
            )
        )

        self.add_dialog(TextPrompt(TextPrompt.__name__))

        self.initial_dialog_id = "WFDialogTranslate"
    

    async def step_select_storage(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("....Sei nella sezione Traduzione... Scegli lo storage")
        iduser=step_context.context.activity.from_property.id
        list=DatabaseManager.getListStorageByID(iduser)
        step_context.values["nome_archivio"]  = DatabaseManager.get_user(iduser).getNomeRg()
        listselect=[]
        for x in list:
            object=CardAction(
                type=ActionTypes.im_back,
                title =x.getStorageName(),
                value=x.getStorageName()
            )
            listselect.append(object)
            
        listselect.append(CardAction(
                type=ActionTypes.im_back,
                title ="Torna Indietro",
                value="back"
            ))
        
        card = HeroCard(
        text ="Ciao,seleziona lo storage... oppure torna al menu principale",
        buttons = listselect)
        
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )

    async def select_file(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result
        if option=="back": 
            return await step_context.end_dialog()
        else:
            name_storage = option
            step_context.values["name_storage"] = name_storage
            storagetemp = DatabaseManager.getStorageByNome(name_storage)
            ACCOUNT_KEY = storagetemp.getKeyStorageDecript(storagetemp.getKeyStorage())
            connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={name_storage};AccountKey={ACCOUNT_KEY}"
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            list = DatabaseManager.getBlobByStorage(name_storage)
            if list is None:
                await step_context.context.send_activity("Non ci sono file da tradurre... inserisci prima il file!!")
                return await step_context.end_dialog()
            listselect=[]
        for x in list:
            object=CardAction(
                type=ActionTypes.post_back,
                title =x.getName(),
                value=x.getName()+"/#/"+x.getNameContainer(),
            )
            listselect.append(object)
        
        card = HeroCard(
        text ="Ciao,seleziona il file da tradurre....",
        buttons = listselect)
        
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )
    
    async def step_lingua(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        nome_blob, name_container = step_context.result.split("/#/")

        #print(nome_blob)
        #print(name_container)

        step_context.values["nome_blob"] = nome_blob
        step_context.values["name_container"] = name_container

        card = HeroCard(
        text ="Seleziona la lingua ....",
        buttons = [
            CardAction(
                type=ActionTypes.im_back,
                title ="Italiano",
                value="it"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Inglese",
                value="in"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Tedesco",
                value="de"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Cinese",
                value="lzh"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Francese",
                value="fr"
            )
        ],   
        )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )
    
    async def step_translate(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        lingua = step_context.result
        nome_blob = step_context.values["nome_blob"] 
        name_container = step_context.values["name_container"]
        name_storage = step_context.values["name_storage"]
        nome_archivio = step_context.values["nome_archivio"]

        blob_client = self.blob_service_client.get_blob_client(container=name_container,blob=nome_blob)
        type = blob_client.get_blob_properties().get("content_settings")["content_type"]

        """creo la key per decifrare"""
        pwd = DatabaseManager.getPassword(name_storage)
        key = Crypt_decrypt.make_password(pwd.encode(),b'10')


        """processo di decifratura file"""
        url = self.get_blob_sas(blob_client.account_name,blob_client.credential.account_key,name_container,nome_blob)
        response = requests.get(url)
        text = response.content
        plaintext = Crypt_decrypt.decrypt(text,key)

        """translate"""
        source_container = self.create_container(self.blob_service_client,nome_archivio+CONFIG.CONTAINER_BLOB_TEMP) #ritorna il container temporaneo
        target_container = self.create_container(self.blob_service_client,"translation-target-container") #creo il container translator oppure restituisce il container translator

        source_container.upload_blob(name=nome_blob,data=plaintext,content_settings=ContentSettings(content_type=type),blob_type="BlockBlob") #carico il file cifrato
        source_container_sas_url = self.generate_sas_url(blob_client,source_container, permissions="rl")
        target_container_sas_url = self.generate_sas_url(blob_client,target_container, permissions="wl")

        if self.translate_sdk(lingua,source_container_sas_url,target_container_sas_url): #effettuo la traduzione
            url = self.get_blob_sas(blob_client.account_name,blob_client.credential.account_key,"translation-target-container",nome_blob)
            await step_context.context.send_activity("Questo è il documento tradotto....")
            await step_context.context.send_activity(MessageFactory.attachment(Attachment(name=nome_blob, content_type=type,content_url=url)))
            #print("key: ",blob_client.credential.account_key)
            #r = requests.get(""+CONFIG.AZURE_FUNCTIONS_ENDPOINT+"?nome_storage="+name_storage+"&container=translation-target-container&"+"blob="+nome_blob+"&accountkey="+blob_client.credential.account_key)
            #print("risposta: ",r.headers,r.status_code,r.reason)
            source_container.delete_blob(blob=nome_blob) #cancello il blob temporaneo
            return await step_context.end_dialog()
        source_container.delete_blob(blob=nome_blob) #cancello il blob temporaneo anche in caso in cui la traduzione da errore
        await step_context.context.send_activity("Impossibile tradurre il file...")
        return await step_context.begin_dialog("WFDialogTranslate")



        
    

       


    @staticmethod
    def create_container(blob_service_client, container_name):
        try:
            container_client = blob_service_client.create_container(container_name)
            print("Creating container: {}".format(container_name))
        except ResourceExistsError:
            print("The container with name {} already exists".format(container_name))
            container_client = blob_service_client.get_container_client(container=container_name)
        return container_client


    
    @staticmethod
    def generate_sas_url(blobclient,container, permissions):
        sas_token = generate_container_sas(
            account_name=blobclient.account_name,
            container_name=container.container_name,
            account_key=blobclient.credential.account_key,
            permission=permissions,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        )
        storage_endpoint = "https://"+blobclient.account_name+".blob.core.windows.net/"
        print("storage endpoint: ",storage_endpoint)
        container_sas_url = storage_endpoint + container.container_name + "?" + sas_token
        print("Generating {} SAS URL".format(container.container_name))
        return container_sas_url


    @staticmethod
    def get_blob_sas(account_name,account_key, container_name, blob_name):
        sas_blob = generate_blob_sas(account_name=account_name, 
                                container_name=container_name,
                                blob_name=blob_name,
                                account_key=account_key,
                                permission=BlobSasPermissions(read=True),
                                expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1))
        url = 'https://'+account_name+'.blob.core.windows.net/'+container_name+'/'+blob_name+'?'+sas_blob
        return url


    @staticmethod
    def translate_sdk(lingua, source, destination):
        client = DocumentTranslationClient(CONFIG.AZURE_TRANSLATION_ENDPOINT, AzureKeyCredential(CONFIG.AZURE_TRANSLATION_KEY))
        poller = client.begin_translation(source, destination, lingua)
        result = poller.result()
        for document in result:
            print("Document ID: {}".format(document.id))
            print("Document status: {}".format(document.status))
            if document.status == "Succeeded":
                return True
            else:
                return False
        




            







