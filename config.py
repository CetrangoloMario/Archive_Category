#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "77956cb5-e08b-42f7-b137-7625e2763199")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "AtLeastSixteenCharacters_0")
    CONNECTION_NAME = os.environ.get("ConnectionName", "ManlioConnection2")

    #Creazione container CAtegoria Standard
    CONTAINER_BLOB_TEMP = "-temp"
    



    #dati di configurazione per l'utilizzo del database SQL
    SERVERDB = 'db-test-archive.database.windows.net'
    DATABASEDB = 'Archivecategorydb'
    USERNAMEDB = 'azureuser'
    PASSWORDDB = 'Mansant#198'
    DRIVERDB= '{ODBC Driver 17 for SQL Server}'
    
