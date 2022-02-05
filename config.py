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

    #dati di configurazione per l'utilizzo del database SQL
    serverdb = 'mysqlservermanlio.database.windows.net'
    databasedb = 'mysampledatabasemanlio'
    usernamedb = 'azureuser'
    passworddb = 'Mansant#198'
    driverdb= '{ODBC Driver 17 for SQL Server}'
    
