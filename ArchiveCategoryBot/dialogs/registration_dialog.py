from contextlib import nullcontext
import imp
from pickle import NONE
import string
from tkinter import dialog
from xmlrpc.client import Boolean
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import CardFactory, MessageFactory
from grapheme import length
from bean.storage import Storage
from bean.container import Container
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.schema._models_py3 import Attachment, CardAction, HeroCard
from botbuilder.schema._connector_client_enums import ActionTypes
from botbuilder.dialogs.prompts.confirm_prompt import ConfirmPrompt
import pyodbc
import os
import re
import json
from botbuilder.dialogs.prompts.choice_prompt import ChoicePrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.choices.list_style import ListStyle
from databaseManager import DatabaseManager
import os, random
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import AzureCliCredential
from bean.user import User
from config import DefaultConfig
from utilities.crypto import Crypto 



CONFIG=DefaultConfig()

class RegistrationDialog(CancelAndHelpDialog): #cancel_and_help_fialog 
    def __init__(self, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)        
        #self.add_dialog(TextPrompt(TextPrompt.__name__, RegistrationDialog.validate))
        self.add_dialog(TextPrompt(TextPrompt.__name__)) #chiedere l'input all'utente 
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [
                    self.select_first, #archivio
                    self.select_second, #creazione oggetti user e storage
                    ]
            )
        )

        self.initial_dialog_id = "WFDialog"


    async def select_first(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Iniziamo la registrazione!")
        #ritorna al Dialog TextPrompt riga 28 
        return await step_context.prompt(
               TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Inserisci il nome dell'archivio ? ")#RG nostro
                ),
            )

    async def select_second(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        rg=step_context.result
        iduser=step_context.context.activity.from_property.id
        
        
        if not self._validate_resource_group(rg): #false se nome resource group non esiste

            await step_context.context.send_activity("....Attendere Prego ci vorr?? pochi secondi.....")

            #generare una password random per la criptazione
            password = self.generate_password()
            crypto = Crypto()
            pwd = crypto.encrypt(password)  #cifro la password

            storage=self.provision_blob(rg,pwd,iduser)
            if storage==None:
                await step_context.context.send_activity("il nome archivio gi?? presente... ricominciamo insieme... ritenta sarai pi?? fortunato")
                return await step_context.begin_dialog("WFDialog")
            else:
                listaStorage=[]
                listaStorage.append(storage)


                utente = User(iduser,rg,listaStorage)
                if DatabaseManager.insert_user(utente):#m if togli
                    if not DatabaseManager.insert_storage(storage): #inserimento storage nel database
                        DatabaseManager.delete_user(utente)
                else:#m
                    await step_context.context.send_activity("utente non inserito... ricominciamo insieme... ritenta sarai pi?? fortunato")#m
                    return await step_context.reprompt_dialog()#m
                
                CONTAINER_TEMP = rg+CONFIG.CONTAINER_BLOB_TEMP
                if not DatabaseManager.insert_container(Container(CONTAINER_TEMP,storage.getStorageName())):
                    await step_context.context.send_activity("container temporaneo non inserito... ricominciamo insieme... ritenta sarai pi?? fortunato")#m
                    DatabaseManager.delete_user(utente)
                    DatabaseManager.delete_storage(storage)
                    return await step_context.reprompt_dialog()#m


                await step_context.context.send_activity("Registrazione Completata !!!")
                return await step_context.end_dialog()
                #step_context.values["utente"] = utente
                
        else:
            await step_context.context.send_activity("Nome archivio esistente !!!")
            return await step_context.begin_dialog("WFDialog")

        

    @staticmethod #return Archivio se account archiviazione creato (Storage), altrimenti None
    def provision_blob(nomeArchivio: str, pwd: str ,id_user: str):
        #print("provisoni blov")
        # Acquire a credential object using CLI-based authentication.
        credential = AzureCliCredential()
        # Retrieve subscription ID from environment variable.
        
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]  #settare azure-subscription-id come variabile d'ambiente
        # Obtain the management object for resources.
        resource_client = ResourceManagementClient(credential, subscription_id)
        
        RESOURCE_GROUP_NAME = nomeArchivio
        availability_result = resource_client
        LOCATION = "westeurope"
        
        rg_result = resource_client.resource_groups.create_or_update(
            RESOURCE_GROUP_NAME,
            {
            "location": LOCATION
            }
        )

        #Provision the storage account, starting with a management object.
        # The name must be 3-24 lower case letters and numbers only.
        storage_client = StorageManagementClient(credential, subscription_id)
        STORAGE_ACCOUNT_NAME = nomeArchivio+f"{random.randint(1,100000):05}"

        availability_result = storage_client.storage_accounts.check_name_availability(
            { "name": STORAGE_ACCOUNT_NAME }
        )

        if not availability_result.name_available:
            print(f"Storage name {STORAGE_ACCOUNT_NAME} is already in use. Try another name.")
            return None
        
        #The name is available, so provision the account
        poller = storage_client.storage_accounts.begin_create(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME,
            {
                "location" : LOCATION,
                "kind": "StorageV2",## possibile in futuro scegliere diversi tipi di storage account e redundacy 
                "sku": {"name": "Standard_LRS"}
            }
        )
        

        account_result = poller.result()
        #print(f"Provisioned storage account {account_result.name}")

        #Retrieve the account's primary access key and generate a connection string.
        keys = storage_client.storage_accounts.list_keys(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME)
        #conn_string = f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={keys.keys[0].value}"

        #print(f"Connection string: {conn_string}")


        # Step 4: Provision the blob container in the account (this call is synchronous)
        CONTAINER_NAME = nomeArchivio+CONFIG.CONTAINER_BLOB_TEMP
        container = storage_client.blob_containers.create(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, {})

    
        if container is None:
            return None



        """cifrare l'account key"""
        crypto = Crypto()
        cipher = crypto.encrypt(keys.keys[0].value)
        
        
        return Storage(STORAGE_ACCOUNT_NAME,cipher,id_user,pwd) 


    @staticmethod #controlla se il nome ?? gi?? presente
    async def _validate_nome_utente(nome_utente: str) -> Boolean:
        utente= DatabaseManager.getUser(nome_utente)
        if utente ==None:
            return True
        else :
            False
    
    @staticmethod #controlla se il nome ?? gi?? presente (false se non ?? presente True se ?? presente)
    def _validate_resource_group(nome: str) -> Boolean:
        return DatabaseManager.aviability_rg(nome)
    
    @staticmethod
    def generate_password():
        length = random.randrange(10,30)

        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        num = string.digits
        symbol = string.punctuation

        all = lower + upper + num+ symbol

        temp = random.sample(all,length)

        return "".join(temp) #ritorna la password


    

        




  
        

       
