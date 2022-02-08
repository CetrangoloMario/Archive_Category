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

    #dati per crittografare il db utilizzaimo l'algoritmo AES (CTR Block Mode)
    SECRET_PASSWORD = "manliokey" #settare secret key in azure
    SECRET_PASSWORD_SALT = "8" #os.urandom(16) 
    SECRET_IV = 256 #secrets.randbits(256) 

    #Creazione container CAtegoria Standard
    CONTAINER_BLOB_TEMP = "-temp"
    



    #dati di configurazione per l'utilizzo del database SQL
<<<<<<< HEAD
    SERVERDB = 'db-test-archive.database.windows.net'
    DATABASEDB = 'Archivecategorydb'
    USERNAMEDB = 'azureuser'
    PASSWORDDB = 'Mansant#198'
=======
    SERVERDB = ''
    DATABASEDB = ''
    USERNAMEDB = ''
    PASSWORDDB = ''
>>>>>>> 6a8ee27f6ca352958b42e9a8d7f68731a28e0ec4
    DRIVERDB= '{ODBC Driver 17 for SQL Server}'
    
