from asyncore import write
from audioop import add
from distutils.file_util import write_file
from lib2to3.pgen2.grammar import opmap
from multiprocessing.sharedctypes import Value
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from bean import container
from bean import user
from databaseManager import DatabaseManager
from bean.user import User
from bean.storage import Storage
from bean.container import Container
from bean.blob import Blob
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__,ContentSettings
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
from azure.storage.blob import ResourceTypes, generate_blob_sas,BlobSasPermissions
from utilities.crypt_decrypt import Crypt_decrypt
from datetime import datetime, timedelta

import uuid, json

from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
)

from config import DefaultConfig
import requests

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
            listselect=[]
        for x in list:
            object=CardAction(
                type=ActionTypes.post_back,
                title =x.getName(),
                value=x.getName()+" "+x.getNameContainer(),
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
        nome_blob, name_container = step_context.result.split()

        print(nome_blob)
        print(name_container)

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
                value="zh-"
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

        """creo un blob temporaneo per la decifratura"""
        blob_plain_text = self.blob_service_client.get_blob_client(container=nome_archivio+CONFIG.CONTAINER_BLOB_TEMP,blob=nome_blob)
        blob_plain_text.upload_blob(plaintext,content_settings=ContentSettings(content_type=type),blob_type="BlockBlob")


        """translate su blob temporaneo"""
        """provare domani la traduzione dei documenti non questa qui testuale"""
        url_sas_source = self.get_blob_sas(blob_plain_text.account_name,blob_plain_text.credential.account_key,nome_archivio+CONFIG.CONTAINER_BLOB_TEMP,nome_blob)
        print("url sorgente: ",url_sas_source)
        """creo un blob temporaneo per la destinazione"""
        blob_destination = self.blob_service_client.get_blob_client(container=nome_archivio+CONFIG.CONTAINER_BLOB_TEMP,blob="translate-"+nome_blob)
        #blob_destination.upload_blob(" ")
        url_sas_target = self.get_blob_sas(blob_destination.account_name,blob_destination.credential.account_key,nome_archivio+CONFIG.CONTAINER_BLOB_TEMP,"translate-"+nome_blob)
        print("url target: ",url_sas_target)

        """translate"""
        #self.translate_document(lingua,url_sas_source,url_sas_target)
        #self.invia_richiesta(lingua,url_sas_source,url_sas_target)
        self.translate_sdk(lingua,url_sas_source,url_sas_target)

        print("testo tradotto: ",blob_destination.download_blob().readall().decode("UTF-8"))

    
    @staticmethod
    def get_blob_sas(account_name,account_key, container_name, blob_name):
        sas_blob = generate_blob_sas(account_name=account_name, 
                                container_name=container_name,
                                blob_name=blob_name,
                                account_key=account_key,
                                permission=BlobSasPermissions(read=True),
                                expiry=datetime.utcnow() + timedelta(hours=1))
        url = 'https://'+account_name+'.blob.core.windows.net/'+container_name+'/'+blob_name+'?'+sas_blob
        return url

    
    @staticmethod
    def translate(lingua, text):
        # Add your subscription key and endpoint
        subscription_key = CONFIG.AZURE_TRANSLATION_KEY
        endpoint = "https://api.cognitive.microsofttranslator.com"

        # Add your location, also known as region. The default is global.
        #This is required if using a Cognitive Services resource.
        location = "westeurope"

        path = '/translate'
        constructed_url = endpoint + path

        params = {
                'api-version': '3.0',
                'to': lingua
            }

        constructed_url = endpoint + path

        headers = {
                'Ocp-Apim-Subscription-Key': subscription_key,
                'Ocp-Apim-Subscription-Region': location,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }

            # You can pass more than one object in body.
        body = [{
                'text': text
            }]

        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        response = request.text
        data = json.loads(response)
        return data[0]["translations"][0]["text"]
    
    @staticmethod
    def translate_document(lingua, sas_url_source, sas_url_target):
        endpoint = "https://traduzionebot.cognitiveservices.azure.com/translator/text/batch/v1.0"
        subscription_key = CONFIG.AZURE_TRANSLATION_KEY
        path = '/batches'
        constructed_url = endpoint + path
        location = "westeurope"

        headers = {
                'Ocp-Apim-Subscription-Key': subscription_key,
                'Ocp-Apim-Subscription-Region': location,
                'Content-type': 'application/json',
            }
        
        payload= {
    "inputs": [
        {
            "storageType": "File",
            "source": {
                "sourceUrl": sas_url_source,
                "storageSource": "AzureBlob"
            },
            "targets": [
                {
                    "targetUrl": "https://manlio58287.blob.core.windows.net/manlio-temp?sp=r&st=2022-02-23T16:28:25Z&se=2022-02-24T00:28:25Z&spr=https&sv=2020-08-04&sr=c&sig=Kqixcsy4uGv54ka8PQNg3cONq3lVAwNkSmwe7LjLztQ%3D",
                    "language": lingua,
                    "storageSource": "AzureBlob",
                    "category": "general"
                }
            ]
        }
    ]
}
        response = requests.post(constructed_url, headers=headers, json=payload)
        print("body: ",response.request.body)
        print("url request: ",response.request.url)
        print("dict: ",response.request.__dict__)

        print(f'response status code: {response.status_code}\nresponse status: {response.reason}\nresponse headers: {response.headers}')


    @staticmethod
    def invia_richiesta(lingua, sas_url_source, sas_url_target):
        host = 'https://traduzionebot.cognitiveservices.azure.com/translator/text/batch/v1.0/batches'
        subscriptionKey =  CONFIG.AZURE_TRANSLATION_KEY
        
        payload= {
    "inputs": [
        {
            "storageType": "File",
            "source": {
                "sourceUrl": sas_url_source,
                "storageSource": "AzureBlob"
            },
            "targets": [
                {
                    "targetUrl": sas_url_target,
                    "language": lingua,
                    "storageSource": "AzureBlob",
                    "category": "general"
                }
            ]
        }
    ]
}
        headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Ocp-Apim-Subscription-Region': "westeurope",
        'Content-type': 'application/json'
        }
        response = requests.post(host, headers=headers, json=payload)
        print(f'response status code: {response.status_code}\nresponse status: {response.reason}\nresponse headers: {response.headers}')

    @staticmethod
    def translate_sdk(lingua, source, destination):
        import os
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.translation.document import DocumentTranslationClient

        client = DocumentTranslationClient("https://traduzionebot.cognitiveservices.azure.com/", AzureKeyCredential(CONFIG.AZURE_TRANSLATION_KEY))

        poller = client.begin_translation(source, "https://manlio58287.blob.core.windows.net/manlio-temp?sp=r&st=2022-02-23T17:49:13Z&se=2022-02-24T01:49:13Z&spr=https&sv=2020-08-04&sr=c&sig=YzX6wLt40nVcZlkr9Eo5bAYAeYya4BWCl%2BSZ%2ByCJ4Qg%3D", lingua)
        result = poller.result()

        print("Status: {}".format(poller.status()))
        print("Created on: {}".format(poller.details.created_on))
        print("Last updated on: {}".format(poller.details.last_updated_on))
        print("Total number of translations on documents: {}".format(poller.details.documents_total_count))

        print("\nOf total documents...")
        print("{} failed".format(poller.details.documents_failed_count))
        print("{} succeeded".format(poller.details.documents_succeeded_count))

        for document in result:
            print("Document ID: {}".format(document.id))
            print("Document status: {}".format(document.status))
            if document.status == "Succeeded":
                print("Source document location: {}".format(document.source_document_url))
                print("Translated document location: {}".format(document.translated_document_url))
                print("Translated to language: {}\n".format(document.translated_to))
            else:
                print("Error Code: {}, Message: {}\n".format(document.error.code, document.error.message))


            







