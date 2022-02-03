from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, PromptValidatorContext, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from databaseManager import DatabaseManager
from bean.user import User
from bean.archivio import Archivio

class CaricaFileDialog(CancelAndHelpDialog):
    
    def __init__(self, dialog_id: str):
        super().__init__(dialog_id)
        self.connection_string = ""
        self.user = User()
        self.add_dialog(
            WaterfallDialog(
                "CaricaFileDialog", [
                    self.select_first,
                    self.select_second
                    ]
            )
        )
    
    async def select_first(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #recuperare storage account e account key
        row = self.user.getStorageAccounteKey(step_context.context.activity.from_property.id)
        print("riga del database: ",row)
        archivio = Archivio(row[0],row[1])
        STORAGE_ACCOUNT_NAME = archivio.getStorageName()
        ACCOUNT_KEY = archivio.getKeyStorage()
        self.connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={ACCOUNT_KEY}"

    


