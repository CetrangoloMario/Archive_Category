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
    APP_ID = os.environ.get("MicrosoftAppId", "e22a9721-53fd-43b6-b910-a9b2ec045e56")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "AtLeastSixteenCharacters_0")
    CONNECTION_NAME = os.environ.get("ConnectionName", "archivecategoryconnection")


    """dati per il classificatore"""
    AZURE_TEXT_ANALYTICS_ENDPOINT = os.environ.get("AZURE_TEXT_ANALYTICS_ENDPOINT","https://westeurope.api.cognitive.microsoft.com/")
    AZURE_TEXT_ANALYTICS_KEY = os.environ.get("AZURE_TEXT_ANALYTICS_KEY","dd6729a862fd44a083e5f49660f33564")
    MULTI_CATEGORY_CLASSIFY_PROJECT_NAME = os.environ.get("MULTI_CATEGORY_CLASSIFY_PROJECT_NAME","classificatordocument")
    MULTI_CATEGORY_CLASSIFY_DEPLOYMENT_NAME = os.environ.get("MULTI_CATEGORY_CLASSIFY_DEPLOYMENT_NAME","prod")

    """dati per l'azure functions"""
    AZURE_FUNCTIONS_ENDPOINT = os.environ.get("AZURE_FUNCTIONS_ENDPOINT","https://deleteblob1.azurewebsites.net/api/deleteblob")

    """dati per il servizio di traduzione"""
    AZURE_TRANSLATION_KEY = os.environ.get("AZURE_TRANSLATION_KEY","b6d97ddb13154aea9a6c712b22f2483b")
    AZURE_TRANSLATION_ENDPOINT = os.environ.get("AZURE_TRANSLATION_ENDPOINT","https://traduzionebot1.cognitiveservices.azure.com/")

    CONVERT_API_SECRET = "i7V5qBfDmNJisc7Z"



    #dati per crittografare il db utilizzaimo l'algoritmo AES (CTR Block Mode)
    SECRET_PASSWORD = "asdf9324dasf90324" #settare secret key in azure
    SECRET_PASSWORD_SALT = "8" #os.urandom(16) 
    SECRET_IV = 256 #secrets.randbits(256) 

    #Creazione container CAtegoria Standard
    CONTAINER_BLOB_TEMP = "-temp" #archivio-temp
    
    


    #dati di configurazione per l'utilizzo del database SQ
    SERVERDB = 'db-test-archive1.database.windows.net'
    DATABASEDB = 'Archivecategorydb'
    USERNAMEDB = 'azureuser'
    PASSWORDDB = 'adsf87#fasdf'
    DRIVERDB= '{ODBC Driver 17 for SQL Server}'
    
