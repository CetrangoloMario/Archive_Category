from contextlib import nullcontext
from xmlrpc.client import Boolean
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import CardFactory, MessageFactory
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




class RegistrationDialog(CancelAndHelpDialog): #cancel_and_help_fialog 
    def __init__(self, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)

        
        #self.add_dialog(TextPrompt(TextPrompt.__name__, RegistrationDialog.validate))
        self.add_dialog(TextPrompt(TextPrompt.__name__)) #chiedere l'input all'utente 
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [
                    self.select_first,
                    self.select_second,
                    self.register]
            )
        )

        self.initial_dialog_id = "WFDialog"


    async def select_first(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Iniziamo la registrazione!")
        #ritorna al Dialog TextPrompt riga 28 
        return await step_context.prompt(
               TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Inserisci il nome dell'archivio ? ")
                ),
            )

    async def select_second(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        print("secondo step registrazione")
        await step_context.context.send_activity("il nome archivio inserito: "+step_context.result)
        if(self.provision_blob(step_context.result)):
            print("account creato !!!")
        else:
            print("account non creato")

        step_context.values["nome_utente"] = step_context.result   

        if not self._validate_nome_utente(step_context.result):
            step_context.values["nome_utente"]==None
            return await step_context.begin_dialog["WFDialog"]

        #form email 
        message_text = ("Inserisci email che sarà usato per i tuoi accessi futuri")
        message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
        await step_context.context.send_activity(message)

        step_context.values["email"]=step_context.result
        

        if not self._validate_email(step_context.result):
            step_context.values["email"]==None
            return await step_context.reprompt_dialog#dubbio reprompt riesegue il dialogo o solo questo passo!! non si capisce si deve eseguire

        


    
    async def register(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        nome_utente=step_context.values["nome_utente"]
        email=step_context.values["email"]
        

        message_text = ("Nome utente inserito è: {}",nome_utente)
        message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
        await step_context.context.send_activity(message)

        DatabaseManager.add_user(nome_utente, email)

        #chiamare azure function per la creazione delle risorse (realizzare un dialog nel caso se servono parametri di configurazione)

        message_text = ("Sei registrato.")
        message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
        await step_context.context.send_activity(message)
        return await step_context.end_dialog()

    @staticmethod #controlla se il nome è già presente
    async def _validate_nome_utente(nome_utente: str) -> Boolean:
        utente= DatabaseManager.getUser(nome_utente)
        if utente ==None:
            return True
        else :
            False



    @staticmethod #controllo email formato /pensare di testare email prima di effettuare la registrazione inviando otp subito.
    async def _validate_email(email: str) -> Boolean:
        reg="(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/"
        if re.match(reg,email) :
            return True
        else :
            False

    @staticmethod #return True account archiviazione creato, altrimenti false
    def provision_blob(nomeArchivio: str) -> Boolean:
        print("provisoni blov")
        # Acquire a credential object using CLI-based authentication.
        credential = AzureCliCredential()
        # Retrieve subscription ID from environment variable.
        print(os.environ)
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]  #settare azure-subscription-id come variabile d'ambiente
        # Obtain the management object for resources.
        resource_client = ResourceManagementClient(credential, subscription_id)
        RESOURCE_GROUP_NAME = "myresourcegroup"
        LOCATION = "westeurope"

        #Provision the storage account, starting with a management object.
        # The name must be 3-24 lower case letters and numbers only.
        storage_client = StorageManagementClient(credential, subscription_id)
        STORAGE_ACCOUNT_NAME = nomeArchivio+f"{random.randint(1,100000):05}"

        availability_result = storage_client.storage_accounts.check_name_availability(
            { "name": STORAGE_ACCOUNT_NAME }
        )

        if not availability_result.name_available:
            print(f"Storage name {STORAGE_ACCOUNT_NAME} is already in use. Try another name.")
            return False
        
        #The name is available, so provision the account
        poller = storage_client.storage_accounts.begin_create(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME,
            {
                "location" : LOCATION,
                "kind": "StorageV2",
                "sku": {"name": "Standard_LRS"}
            }
        )

        account_result = poller.result()
        print(f"Provisioned storage account {account_result.name}")

        #Retrieve the account's primary access key and generate a connection string.
        keys = storage_client.storage_accounts.list_keys(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME)
        conn_string = f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={keys.keys[0].value}"
        print(f"Connection string: {conn_string}")

        return True



  
        

       
