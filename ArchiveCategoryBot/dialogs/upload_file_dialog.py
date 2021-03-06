
from cgitb import text
from distutils.command.config import config
from fnmatch import translate
from pydoc import plain
from sqlite3 import IntegrityError
from aiohttp import request
import os
from grapheme import contains, length
import databaseManager
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
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
from datetime import datetime, timedelta
from azure.storage.blob import ResourceTypes, generate_blob_sas,BlobSasPermissions
import requests, uuid, json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from utilities.classificatordocument import ClassificatorDocument
from azure.mgmt.resource import ResourceManagementClient
from config import DefaultConfig
from utilities.crypt_decrypt import Crypt_decrypt
import convertapi
CONFIG = DefaultConfig

#passi utente carica il file, poi viene categorizzato dal servizio machine learning, (serve blob temporaneo)
#dopo averlo caricato dialogo per inserire alcuni tag da stabilire, compressione cripto e cancellazione del file temporaneo.
#utente carica il file, viene categorizzato se utente accetta la categoria ok se no si deve far scegliere utente tra le categorie gia preseti 
#cio?? container gi?? creati standard e dall'utente personali oppure dare la possibilit?? di creare uno nuovo.

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
                    self.step_choice_category,#scelta tra categorie esistenti o crea una nuova"""
                    self.step_choice, #scelta utente ok va a WFDialogOption altrimenti va nello step successivo
                    self.step_create_container, #l'utente crea il nuovo container
                    self.step_final
                    ]
            )
        )

        self.add_dialog(AttachmentPrompt(AttachmentPrompt.__name__)) #,Upload_file_dialog.file_prompt_validator))   #prendere il file in input
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__)) #prende la risposta dell'utente si o no
        self.add_dialog(TextPrompt(TextPrompt.__name__)) #chiedere l'input all'utente 



        """
        self.add_dialog(
            WaterfallDialog(
                "WFDialogOption", [
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
        
        if user is None:
            return await step_context.cancel_all_dialogs()
        
        RG=user.getNomeRg()
        #print (RG,"")
        
        """recupero lista storage account"""
        
        list=DatabaseManager.getListStorageByID(iduser)
        if list is None:
            await step_context.context.send_activity(" Errore Non trovata lista Archivio ripeti login")
            return await step_context.cancel_all_dialogs()
        
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
        #print("sto in upload")
        file = step_context.result[0]  #prelevo il file ?? un dict
        
        ris = requests.get(file.__dict__["content_url"])

        contenuto = ris.content
        #file_bytes.close()

        #print("file: ",file)
        step_context.values["document"] = file
        nome_blob = file.__dict__["name"] #prelevare il nome del file
        #print("Nome blob: ",nome_blob)
        if nome_blob is None:
            await step_context.context.send_activity("Errore Name File rieffettua upload")
            return await step_context.reprompt_dialog()
        
        step_context.values["name-blob"] = nome_blob #salvo in sessione

        iduser=step_context.context.activity.from_property.id
        user = databaseManager.DatabaseManager.get_user(iduser)
        if user is None:
            await step_context.context.send_activity("Errore prelevamento dati utente Session Expired")
            return await step_context.cancel_all_dialogs()
        
        self.rg = user.getNomeRg()  #salvo il container temporaneo
        NAMESTORAGE=step_context.values["select_storage"]
        self.nome_storage = NAMESTORAGE
        #key
        storagetemp = DatabaseManager.getStorageByNome(NAMESTORAGE)
        
        if storagetemp is None: 
            await step_context.context.send_activity("Errore prelevamento Archivio temporaneo")
            return await step_context.cancel_all_dialogs()
        
        ACCOUNT_KEY = storagetemp.getKeyStorageDecript(storagetemp.getKeyStorage())

        self.connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={NAMESTORAGE};AccountKey={ACCOUNT_KEY}"
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        #modificare (id , storage accout selezionato) lista container
        name_container_temp= DatabaseManager.getContainerbyName(NAMESTORAGE,user.getNomeRg()+CONFIG.CONTAINER_BLOB_TEMP)
        step_context.values["name-container"] = name_container_temp.getNameContainer()
        try:
            blob_client = self.blob_service_client.get_blob_client(container=name_container_temp.getNameContainer(), blob=nome_blob)
            blob_client._set_blob_tags_options()
        except AttributeError:
            await step_context.context.send_activity("....File duplicato....")
            return await step_context.reprompt_dialog()
        #print("url: ",file.__dict__["content_url"])

        blob_client.upload_blob(contenuto,blob_type="BlockBlob",content_settings=ContentSettings(content_type=file.__dict__["content_type"]))

        await step_context.context.send_activity("....File caricato con successo nel container temporaneo.....")

        return await step_context.next(1)



    
    async def step_category(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("....Categorizziamo il file appena caricato.....")

        container = step_context.values["name-container"] #container temporaneo
        self.container = container #salvo in una variabile d'istanza il nome del container temporaneo
        blob = step_context.values["name-blob"]
        self.blob = blob #salvo in una variabile d'istanza il nome del file inserito
        blob_client = self.blob_service_client.get_blob_client(container=container,blob=blob) #prelevo il blob appena caricato
        property = blob_client.get_blob_properties()
        #fare if se non ?? txt file chiamare un azure function in cui converte il file e restituisce il contenuto
        if property.get("content_settings")["content_type"] == "text/plain":
            text = blob_client.download_blob().readall().decode("UTF-8") 
        else:
            root, ext = os.path.splitext(blob)
            convertapi.api_secret = CONFIG.CONVERT_API_SECRET
            url = self.get_blob_sas(blob_client.account_name,blob_client.credential.account_key,container,blob)
            try:
                file=convertapi.convert('txt', {'File': url}, from_format = ext[1:]) #.save_files('./utilities/document.txt')# prendere contenuto
                #print(file.file.url)
                ris = requests.get(file.file.url)
                text = ris.content.decode("UTF-8")
            except convertapi.exceptions.ApiError:
                await step_context.context.send_activity("il file caricato non ?? possibile classificarlo.....Scegli tra le categorie disponibili oppure crea una nuova categoria")
                return await step_context.next(False)
           
        
        #myblob deve essere passato al machine learnig
        try:
            classificator = ClassificatorDocument()
            self.category, score = classificator.classificatorcategory(text) 
            score = 100*score #per avere la percentuale da 0 a 100
            step_context.values["value_category"] = score
        except Exception:
             await step_context.context.send_activity("il file caricato non ?? possibile classificarlo.....Scegli tra le categorie disponibili oppure crea una nuova categoria")
             return await step_context.next(False)
           
        if score <=55:
            await step_context.context.send_activity("Il file ?? stato categorizzato ma non ha superato la soglia di consolidamneto: ",self.category)
            await step_context.context.send_activity("Scegli tra le categorie disponibili oppure crea una nuova categoria")
            return  await step_context.next(False)
        else:
            await step_context.context.send_activity("il file appena caricato ?? stato categorizzato come: "+self.category)
            return await step_context.prompt(
               ConfirmPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Per lei conferma questa categoria(digita Yes) oppure vuoi creare una nuova (digita No) ??")
                ),
             )
    

    
    async def step_choice_category(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        risposta = step_context.result
        nome_container_temp=step_context.values["name-container"]
        nome_storage = step_context.values["select_storage"]
        listaContainers = DatabaseManager.getContainerByNameStorage(nome_storage)
        if risposta == True:     #inserire il file nella categoria scelta dal classificatore
            step_context.values["risposta"] = "yes" #controllare se il contentiore (categoria) ?? stata gia creata controllo nello step finale
            step_context.values["listaContainer"] = listaContainers
            return await step_context.next(1)
        else:   #l'utente deve creare una nuova categoria oppure selezione una container gia esistente
            step_context.values["risposta"] = "no"
            listaContainers = DatabaseManager.getContainerByNameStorage(nome_storage)  #prelevo tutti i container esistenti
            step_context.values["listaContainer"] = listaContainers
            listselect = []
            for x in listaContainers:
                #print("x: ",x)
                if x == nome_container_temp:
                    break
                object=CardAction(
                    type=ActionTypes.im_back,
                    title =x,
                    value=x
                )
                listselect.append(object)
            
            listselect.append(CardAction(
                type=ActionTypes.im_back,
                title ="New container",
                value="newContainer"
                ))
        
            card = HeroCard(
                     text ="Ciao,seleziona le categorie esistenti oppure creare una nuova.",
                     buttons = listselect)
        
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
                ),
            )


           

    
    async def step_choice(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option=step_context.result  #la scelta dell'utente
        listacontainer=step_context.values["listaContainer"]

        if(option=="newContainer"):
             return await step_context.prompt(
               TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Inserisce il nome della nuova categoria ??")
                ),
                )
        else:
            category = step_context.result
            if(step_context.values["risposta"] == "yes"):  #se l'utente digita yes sopra allora prendo la categoria salvata come variabili d'istanza la categoria scelta dal classificatore 
                await step_context.context.send_activity("Hai Confermato la categoria predetta: "+self.category)
                return await step_context.next(None)
            
            else: #altrimenti devo aggiornare la variabile d'istanza e mettere la categoria selezionata dall'utente
                self.category = category
                await step_context.context.send_activity("Hai selezionato la categoria: "+self.category)
                return await step_context.next(None)
    
    async def step_create_container(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        listacontainer=step_context.values["listaContainer"]

        if step_context.result is None:
            nome_categoria=self.category
            #print("nome categoria: ",nome_categoria)
        else:
            nome_categoria= step_context.result
            #print("nome categoria else: ",nome_categoria)
            self.category=nome_categoria
            
        #await step_context.context.send_activity("Creiamo la nuova categoria: "+nome_categoria)
        #inserire nel db la nuova categoria (controllare lerrore nel caso in cui la categoria inserita gi?? esiste)
        #creare anche nello storage account la categoria
        if not self.category in listacontainer:
            self.blob_service_client.create_container(nome_categoria)
            container = Container(nome_categoria,step_context.values["select_storage"])
            
            if DatabaseManager.insert_container(container):
                await step_context.context.send_activity("La categoria ?? stata creata ")
            else:
                await step_context.context.send_activity("La categoria non ?? stata creata ")
            
        else:
            await step_context.context.send_activity("la categoria gia ?? presente")

        self.category = nome_categoria 
        return await step_context.next(1)
    

    async def step_final(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #cointaner=self.category
        nome_blob=self.blob#temporaneo

        """#prelevo il blob appena caricato nel container temporaneo e prelevo anche il content-type"""
        blob_temp = self.blob_service_client.get_blob_client(container=self.rg+CONFIG.CONTAINER_BLOB_TEMP,blob=nome_blob) 
        type = blob_temp.get_blob_properties().get("content_settings")["content_type"]

        """costruisco la key per cifratura"""
        pwd = DatabaseManager.getPassword(self.nome_storage)
        key = Crypt_decrypt.make_password(pwd.encode(),b'10')

        """Processo di cifratura e inserisco il blob nel container selezionato"""
        url = self.get_blob_sas(blob_temp.account_name,blob_temp.credential.account_key,self.rg+CONFIG.CONTAINER_BLOB_TEMP,nome_blob)
        response = requests.get(url)
        text = response.content
        cipher = Crypt_decrypt.encrypt(text,key)
        blob_client = self.blob_service_client.get_blob_client(container=self.category, blob=nome_blob)
        blob_client.upload_blob(cipher,content_settings=ContentSettings(content_type=type),blob_type="BlockBlob")

        """cancello il blob temporaneo"""
        try:
            blob_temp.delete_blob()
        except:
            await step_context.context.send_activity("cancellazione file temporaneo non eseguita. Sar?? svolta in seguito")
            
            
        """sincronizzare con il database"""
        blob=Blob(self.blob,self.category,None,None)
        
        if DatabaseManager.insert_blob(blob):
            await step_context.context.send_activity("Upload del file completato...torna al menu principale")
        else:
            await step_context.context.send_activity("Sincronizzazione Database non effettuata")
        #step_context.values["skip"] =True
        return await step_context.end_dialog() #ritorna al main dialog step final step
        

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
                if attachment.content_type in ["text/plain","pdf"] 
        ]

        prompt_context.recognized.value = valid_images
        return len(valid_images) > 0

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

    






        



        

        


    

