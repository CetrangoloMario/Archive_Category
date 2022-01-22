#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "77956cb5-e08b-42f7-b137-7625e2763199")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "dbc5c99f-bb35-41ac-9723-fcf02a476b51")
    CONNECTION_NAME = os.environ.get("ConnectionName", "ManlioConnection")
    
