from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import CardFactory, MessageFactory
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.schema._models_py3 import Attachment, CardAction, HeroCard
from botbuilder.schema._connector_client_enums import ActionTypes
import pyodbc
import os
import json
from botbuilder.dialogs.prompts.choice_prompt import ChoicePrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.choices.list_style import ListStyle
from databaseManager import DatabaseManager


CATEGORIES=DatabaseManager.find_categories()
for cat in CATEGORIES:
    if cat.name == "Genere sconosciuto":
        CATEGORIES.remove(cat)

class RegistrationDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)

        
        self.add_dialog(TextPrompt(TextPrompt.__name__, RegistrationDialog.validate))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.select_first,
                    self.select_second,
                    self.select_third,
                    self.register]
            )
        )

        self.initial_dialog_id = "WFDialog"


    async def select_first(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        card=self.create_card(step_context)

        #form nome utente
        #email
        
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt = MessageFactory.attachment(card),
                retry_prompt= MessageFactory.text("Inserisci una categoria valida.")
            )
        )     


    
    async def register(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result = step_context.result
        selected = step_context.values["selected"]

        message_text = ("")
        message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
        await step_context.context.send_activity(message)
        iduser=step_context.context.activity.from_property.id
        DatabaseManager.add_user(iduser, selected)
        message_text = ("Sei registrato.")
        message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
        await step_context.context.send_activity(message)
        return await step_context.end_dialog()

    

  
        

       
