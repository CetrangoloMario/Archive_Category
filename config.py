#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from re import S
import secrets

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "77956cb5-e08b-42f7-b137-7625e2763199")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "AtLeastSixteenCharacters_0")
    CONNECTION_NAME = os.environ.get("ConnectionName", "ManlioConnection2")


    """dati per il classificatore"""
    AZURE_TEXT_ANALYTICS_ENDPOINT = os.environ.get("AZURE_TEXT_ANALYTICS_ENDPOINT","https://westeurope.api.cognitive.microsoft.com/")
    AZURE_TEXT_ANALYTICS_KEY = os.environ.get("AZURE_TEXT_ANALYTICS_KEY","6219ebc9404a4bb698b9bcb55da134f5")
    MULTI_CATEGORY_CLASSIFY_PROJECT_NAME = os.environ.get("MULTI_CATEGORY_CLASSIFY_PROJECT_NAME","classificatordocument")
    MULTI_CATEGORY_CLASSIFY_DEPLOYMENT_NAME = os.environ.get("MULTI_CATEGORY_CLASSIFY_DEPLOYMENT_NAME","trainingcategory")





    #dati per crittografare il db utilizzaimo l'algoritmo AES (CTR Block Mode)
    SECRET_PASSWORD = "manliokey" #settare secret key in azure
    SECRET_PASSWORD_SALT = "8" #os.urandom(16) 
    SECRET_IV = 256 #secrets.randbits(256) 

    #Creazione container CAtegoria Standard
    CONTAINER_BLOB_TEMP = "-temp" #archivio-temp
    
    


    #dati di configurazione per l'utilizzo del database SQ
    SERVERDB = 'db-test-archive.database.windows.net'
    DATABASEDB = 'Archivecategorydb'
    USERNAMEDB = 'azureuser'
    PASSWORDDB = 'Mansant#198'
    DRIVERDB= '{ODBC Driver 17 for SQL Server}'
    
