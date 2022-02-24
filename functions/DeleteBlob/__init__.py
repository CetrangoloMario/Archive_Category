import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    nome_storage = req.params.get('nome_storage')
    account_key = req.params.get("accountkey")
    nome_container = req.params.get('container')
    nome_blob = req.params.get('blob')
    if not nome_storage or nome_container or nome_blob or account_key:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            nome_storage = req_body.get('nome_storage')
            nome_container = req_body.get('container')
            nome_blob = req_body.get('blob')
            account_key = req.params.get("accountkey")

    if nome_storage and nome_container and nome_blob and account_key:
        logging.info(nome_storage+nome_container+nome_blob)

        cancel_blob(nome_storage,account_key,nome_container,nome_blob)
        return func.HttpResponse("blob eliminato")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

def cancel_blob(nome_storage,account_key,nome_cointainer,nome_blob):
    logging.info("funzione: "+nome_storage+nome_cointainer+nome_blob)
    connection_string =f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={nome_storage};AccountKey={account_key}"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=nome_cointainer,blob=nome_blob)
    blob_client.delete_blob()

    


