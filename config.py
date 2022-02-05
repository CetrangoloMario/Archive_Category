#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    CONNECTION_NAME = os.environ.get("ConnectionName", "")

    #Creazione container CAtegoria Standard
    CONTAINER_BLOB_TEMP = "_TEMP"
    



    #dati di configurazione per l'utilizzo del database SQL
    SERVERDB = 'mysqlservermanlio.database.windows.net'
    DATABASEDB = 'mysampledatabasemanlio'
    USERNAMEDB = 'azureuser'
    PASSWORDDB = 'Mansant#198'
    DRIVERDB= '{ODBC Driver 17 for SQL Server}'
    
