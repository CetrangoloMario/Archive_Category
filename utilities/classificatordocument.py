import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
        TextAnalyticsClient,
        MultiCategoryClassifyAction
    )

f




from config import DefaultConfig

config = DefaultConfig()

class ClassificatorDocument():

    def __init__(self):
        self.client = self.authenticate_client()
    
    def authenticate_client(self):
        text_analytics_client = TextAnalyticsClient(
        endpoint=config.AZURE_TEXT_ANALYTICS_ENDPOINT,
        credential=AzureKeyCredential(config.AZURE_TEXT_ANALYTICS_KEY))
        return text_analytics_client
    

    def classificatorcategory(self,file):

        document = [file.read]
        
        print("document: ",document)

        poller = self.client.begin_analyze_actions(
        document,
        actions=[
            MultiCategoryClassifyAction(
                project_name=config.MULTI_CATEGORY_CLASSIFY_PROJECT_NAME,
                deployment_name=config.MULTI_CATEGORY_CLASSIFY_DEPLOYMENT_NAME
            ),
        ],
    )
        print("poller dopo")

        document_results = poller.result()
        for doc, classification_results in zip(document, document_results):
            for classification_result in classification_results:
                if not classification_result.is_error:
                    classifications = classification_result.classifications
                    print(f"\nThe document plot '{doc}' was classified as the following genres:\n")
                    for classification in classifications:
                        print("'{}' with confidence score {}.".format(
                        classification.category, classification.confidence_score
                        ))
                else:
                    print("document plot '{}' has an error with code '{}' and message '{}'".format(
                    doc, classification_result.code, classification_result.message
                ))


         
        