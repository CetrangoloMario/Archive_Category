# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from cmath import log
from distutils.log import Log
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, DialogTurnStatus, WaterfallDialog, WaterfallStepContext
from botbuilder.schema import (
    ChannelAccount,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.core import MessageFactory, TurnContext, CardFactory, UserState
from botbuilder.schema import Attachment, InputHints, SuggestedActions
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.prompts.oauth_prompt_settings import OAuthPromptSettings
from botbuilder.dialogs.prompts.oauth_prompt import OAuthPrompt
from botbuilder.dialogs.prompts.confirm_prompt import ConfirmPrompt
from botbuilder.dialogs.choices.channel import Channel
from .registration_dialog import RegistrationDialog
from databaseManager import DatabaseManager
from botbuilder.schema._connector_client_enums import ActivityTypes
from botbuilder.dialogs.dialog import Dialog
from botbuilder.core import BotFrameworkAdapter
from dialogs.upload_file_dialog import Upload_file_dialog
from dialogs.download_file_dialog import Download_file_dialog
from bean import *
import os
import json
from typing import Dict

registration_dialog = RegistrationDialog()
upload_file_dialog  = Upload_file_dialog()
download_file_dialog = Download_file_dialog() 

class MainDialog(ComponentDialog):
    
    def __init__(self, connection_name: str, conversation_state):
        super(MainDialog, self).__init__(MainDialog.__name__)
        self.connection_name=connection_name
        self.registration_dialog_id=registration_dialog.id
        self.upload_file_dialog = upload_file_dialog.id
        self._download_file_dialog = download_file_dialog.id
    
        self.add_dialog(
            OAuthPrompt(
                OAuthPrompt.__name__,
                OAuthPromptSettings(
                    connection_name=connection_name,
                    text="Accedi",
                    title="Sign In",
                    timeout=300000,
                ),
            )
        )

        self.add_dialog(TextPrompt(TextPrompt.__name__)) #chiede all'utente l'input
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__)) #Richiede a un utente di confermare qualcosa con una risposta sì/no.
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", 
                [
                 self.menu_step, 
                 self.option_step,
                 self.final_step, 
                 self.loop_step]
            )
        )
        
        self.add_dialog(registration_dialog)

        self.add_dialog(upload_file_dialog)

        self.add_dialog(download_file_dialog)
    
        self.add_dialog(
            WaterfallDialog(
                "WFDialogLogin",
                [
                    self.prompt_step,
                    self.login_step,
                    self.continue_step
                ]
            )
        )
        
        self.initial_dialog_id = "WFDialogLogin"
        self.conversation_state=conversation_state

        
        

    async def prompt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        welcome_card = self.create_welcome_card()
        #print("welcome card")
        await step_context.context.send_activity(welcome_card)
        return await step_context.begin_dialog(OAuthPrompt.__name__)
        

    async def login_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["skip"] = False
        #richieste all'utente username wilcard
        if step_context.result:
            iduser=step_context.context.activity.from_property.id
            #print("iduser: ",iduser)
            await step_context.context.send_activity("Hai inserito il codice!!! controllo se sei registrato!!!!")
            
            if not DatabaseManager.user_is_registered(iduser):
                await step_context.context.send_activity(MessageFactory.text('''Non sei registrato'''))
                return await step_context.begin_dialog(self.registration_dialog_id) 
            else:
                #nome resource group (nomr archivio ) preleva da db
                loginuser = DatabaseManager.get_user(iduser)
                if loginuser is not None:
                    print(loginuser.getNomeRg)
                    step_context.values["RG"] = loginuser.getNomeRg()
                await step_context.context.send_activity(MessageFactory.text('''Login effetuato'''))
                return await step_context.next([])
        else:
            await step_context.context.send_activity("Il login non è andato a buon fine. Riprova.")
            return await step_context.end_dialog()
    
   


    async def continue_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.begin_dialog("WFDialog")
        
    
    async def menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #Dialog.resume_dialog(step_context,)
        step_context
        card = HeroCard(
        text ="Ciao, come posso aiutarti? Per uscire digita quit o esci.",
        buttons = [
            CardAction(
                type=ActionTypes.im_back,
                title ="Info",
                value="info"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Logout",
                value="logout"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Carica File",
                value="caricaFile"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Scarica File",
                value="scaricaFile"
            )
        ],   
        )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )
    
    async def option_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option=step_context.result
        
        if option=="info": ## Riassunto account dimensione storage ....
            info_card = self.create_adaptive_card_attachment()
            resp = MessageFactory.attachment(info_card)
            await step_context.context.send_activity(resp)
            return await step_context.next([])

        if option=="caricaFile":
            await step_context.context.send_activity("hai scelto caricafile")
            return await step_context.begin_dialog(self.upload_file_dialog)

        if option=="scaricaFile":
            await step_context.context.send_activity("hai scelto visualizzafile")
            return await step_context.begin_dialog(self._download_file_dialog)

        if option=="logout": 
            bot_adapter: BotFrameworkAdapter = step_context.context.adapter
            await bot_adapter.sign_out_user(step_context.context, self.connection_name)
            await step_context.context.send_activity("Sei stato disconnesso.")
            return await step_context.cancel_all_dialogs()

        
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        try:
            skip = step_context.values["skip"]
        except KeyError:
            skip = False
            step_context.values["skip"] =False
        if not skip:
            message_text = "Posso fare qualcos'altro per te?"
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            return await step_context.prompt(
                ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        else:
            step_context.values["skip"] = False
            return await step_context.next(True)


    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=step_context.result
        if result:
            return await step_context.replace_dialog("WFDialog")
        return await step_context.cancel_all_dialogs()

    
        
    def create_welcome_card(self):
        title = "Benvenuto in ArchiveCategory"
        subtitle = "Per iniziare ad utilizzare il bot effettuare il login"
        #image = CardImage(url="https")
        card = HeroCard(title=title, subtitle=subtitle,images=None)
        activity = MessageFactory.attachment(CardFactory.hero_card(card))
        return activity
    