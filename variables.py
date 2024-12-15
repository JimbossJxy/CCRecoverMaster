"""
    Created at 16:00:00 on 10/11/2024
    File name: variables.py
    Description:
        This file is responsible for storing all the necessary variables.
        This file will be responsible for the following:
            - Storing all the necessary variables
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pathlib import Path


settings = {
        "settings": {
            'keys': { # At the moment the certificates aren't being used but they can be used for future implementations - Not too hard to implement
                "sslcrt": str(Path.home() / "node" / "certs" / "cert.pem"), # Modify this for your own SSL certificate
                "sslkey": str(Path.home() / "node" / "keys" / "key.pem"), # Modify this for your own SSL key
                "ca": str(Path.home() / "node" / "certs" / "ca.pem"), # Modify this for your own CA certificate
            },
            'port': 443, # HTTPS port
            'reciepientEmails': ['email@address', 'email@address'], # Update to your own email/'s 
            'credentialsLocation': str(Path.home() / "node" / "credentials.json"),
            'masterEmail': 'email@address', # Update to the email you want to send the emails from
            'queueSize': 25, # The amount of passwords to generate - bigger the number the more passwords will be generated which can be good for a large network but can have a performance impact
            'amountOfPasswordsPerJsonFile': 1000, # The amount of passwords to generate per json file
    },
}
# all information about the master node
masterInfo = {
    'onlineNodes': 0, # Number of internal nodes connected # Number of external nodes connected
    'lastGeneratedPassword': 'a', # Last password generated
    'lastSentPassword': 'a', # Last password sent
    'lastCheckedPassword': 'a', 
    'amountOfPasswordsChecked': 0,
    'amountOfPasswordsGenerated': 0,
    "lastCheckedPasswordTime":0 # Unix timestamp
}

# weekly information
weeklyInfo = {
    'weeklyOnlineNodes': 0, # Number of internal nodes connected # Number of external nodes connected
    'weeklyLastGeneratedPassword': 'a', # Last password generated
    'weeklyLastSentPassword': 'a', # Last password sent
    'weeklyLastCheckedPassword': 'a',
    'weeklyLastCheckedPasswordTime': 0, # Unix timestamp
    'weeklyAmountOfPasswordsChecked': 0,
    'weeklyAmountOfPasswordsGenerated': 0,
    'weeklyLastTimeChecked': 0,
}


sendDataPacket = {
    "packetInfo": {
        "node_id": "Master",
        "status": "True",
        "sendData": "True",
        "lastGeneratedPassword": "a",
        "nextMasterRestart": 0, # Unix timestamp
        
    },
    "passwords": [],
}

nodes = {
    "online": [],
    "offline": []
}

found = False
serverShutdown = False
# Paths
defaultPath = str(Path.home() / "node")
settingsPath = str(Path.home() / "node" / "settings")
settingsFilePath = str(Path.home() / "node" / "settings" / "settings.ini")
queuePath = (Path.home() / "node" / "queue")
certPath = str(Path.home() / "node" / "certs")
keyPath = str(Path.home() / "node" / "keys")
logPath = str(Path.home() / "node" / "logs")
weeklyPath = str(Path.home() / "node" / "weekly.json")
saveDataPath = str(Path.home() / "node" / "saveData.json")
nodePath = str(Path.home() / "node" / "nodes.json")





for path in [defaultPath, settingsPath, queuePath, certPath, keyPath, logPath ]:
    if not os.path.exists(path):
        os.makedirs(path)

# update the weekly data