import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    nome_storage = req.params.get('nome_storage')
    account_key = req.params.get("accountkey")
    nome_archivio = req.params.get('nomearchivio')
    if not nome_storage or not nome_archivio or not account_key:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            nome_storage = req_body.get('nome_storage')
            account_key = req.params.get("accountkey")
            nome_archivio = req_body.get('nomearchivio')

    if nome_storage and nome_archivio and account_key:
        cancel_blob(nome_storage,account_key,nome_archivio)
        return func.HttpResponse("blob eliminato")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

def cancel_blob(nome_storage,account_key,nome_archivio):
    connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={nome_storage};AccountKey={account_key}"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_temporaneo = blob_service_client.get_container_client(container=nome_archivio+"-temp")
    #container_temp_translate = blob_service_client.get_container_client(container="translation-target-container")
    listblob = container_temporaneo.list_blobs()
    if listblob is not None:
        for file in listblob:
           container_temporaneo.delete_blob(blob=file.name)

    try:
        container_temp_translate = blob_service_client.get_container_client(container="translation-target-container")
        listblob = container_temp_translate.list_blobs() 
        if listblob is not None:
            for file in listblob:
                container_temp_translate.delete_blob(blob=file.name)
    except Exception:
      return func.HttpResponse("Container non creato",status_code=200)

    





    


