from typing import List

from grapheme import length
from bean import *
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
from .main_dialog import MainDialog
    
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
main_dialog=MainDialog()

""" chiedere all'utente il nome del file da visualizzare, altrimenti percoso storage account select
container select, stampo la lista dei nomi dei blob"""
class View_file_dialog(ComponentDialog):

    
    def __init__(self, dialog_id: str = None):
        super(View_file_dialog,self).__init__(dialog_id or View_file_dialog.__name__)   
        self.connection_string = ""
        self.user = User()
        self.storage=Storage()
        self.container= Container()
        self.blob= Blob()
        
        self.add_dialog(
            WaterfallDialog(
                "WFViewFile", [
                    self.step_initial, 
                    self.step_view_file,
                    self.step_view_container,
                    self.step_view_storage,
                    #Step successivo dipende dalla scelta se cancellare il file, scaricarlos

                    ]
            )
        )
        
        self.initial_dialog_id="WFViewFile"

    async def step_initial(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        await step_context.context.send_activity("....Sei nella sezione Visualizza file... Inizia ad inserire il nome di un file")
        message_text = "Inserisci nome file: \n"
        prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
        return await step_context.prompt(
                ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        
    async def step_view_file(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        nomeFile= step_context.result
        
        listFile=[]
        listFile=DatabaseManager.getBlobByName(nomeFile)
        
        if listFile is None:
            await step_context.context.send_activity(" File non trovato ")
            return await step_context.reprompt_dialog()
        
        elif len(listFile)<2:
            await step_context.context.send_activity(" File trovato un solo elemento")
            #funzione download file
            return await step_context.begin_dialog(main_dialog.begin_dialog("WFDialog"))
        
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
        )
            
        
        
    
    async def step_select_storage(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        nameFile=step_context.result
        
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
        
        
    
    
     