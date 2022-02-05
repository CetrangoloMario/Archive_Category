from contextlib import nullcontext
from tkinter import dialog
from xmlrpc.client import Boolean
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import CardFactory, MessageFactory
from bean.archivio import Archivio
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




class RegistrationDialog(CancelAndHelpDialog): #cancel_and_help_fialog 
    def __init__(self, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)        
        #self.add_dialog(TextPrompt(TextPrompt.__name__, RegistrationDialog.validate))
        self.add_dialog(TextPrompt(TextPrompt.__name__)) #chiedere l'input all'utente 
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [
                    self.select_first,
                    self.select_second
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
        step_context.values["archivio"] = step_context.result
        nome_archivio = step_context.result
        iduser=step_context.context.activity.from_property.id
        
        if not self._validate_resource_group(nome_archivio): #false se nome resource group non esiste
            rg = nome_archivio

            await step_context.context.send_activity("....Attendere Prego ci vorrà pochi secondi.....")
            arc=self.provision_blob(nome_archivio)
            if arc==None:
                await step_context.context.send_activity("il nome archivio già presente... ricominciamo insieme... ritenta sarai più fortunato")
                return await step_context.begin_dialog("WFDialog")
            else:
                listarchive=list()
                listarchive.append(arc)

                DatabaseManager.insert_archivio(arc) #inserimento archivio nel database
                
                utente = User(iduser,nome_archivio,arc.getStorageName(),arc.getKeyStorage())

                if not DatabaseManager.insert_user(utente): #inserimento utente nel database
                    #delete dati database errore query inserimento
                    DatabaseManager.delete_archivio(arc)
                    

                await step_context.context.send_activity("Registrazione Completata !!!")
                return await step_context.end_dialog()
                #step_context.values["utente"] = utente
                print("account creato\n ")
        else:
            await step_context.context.send_activity("Nome archivio esistente !!!")
            return await step_context.begin_dialog("WFDialog")

        

    @staticmethod #return Archivio se account archiviazione creato, altrimenti None
    def provision_blob(nomeArchivio: str):
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
            "location": "westeurope"
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
                "kind": "StorageV2",
                "sku": {"name": "Standard_LRS"}
            }
        )

        account_result = poller.result()
        #print(f"Provisioned storage account {account_result.name}")

        #Retrieve the account's primary access key and generate a connection string.
        keys = storage_client.storage_accounts.list_keys(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME)
        #conn_string = f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={keys.keys[0].value}"
        #print(f"Connection string: {conn_string}")
        return Archivio(STORAGE_ACCOUNT_NAME,keys.keys[0].value) 


    @staticmethod #controlla se il nome è già presente
    async def _validate_nome_utente(nome_utente: str) -> Boolean:
        utente= DatabaseManager.getUser(nome_utente)
        if utente ==None:
            return True
        else :
            False
    
    @staticmethod #controlla se il nome è già presente (false se non è presente True se è presente)
    def _validate_resource_group(nome: str) -> Boolean:
        return DatabaseManager.aviability_rg(nome)
    

        




  
        

       
