"""
    Created at 19:43:00 on 09/11/2024
    File name: logging.py
    Description:
        This file is responsible for logging all the necessary information.
        This file will be responsible for the following:
            - Logging all the necessary information
"""

# Importing the necessary libraries



import logging
import logging.config
from pathlib import Path
from logging.handlers import RotatingFileHandler
from variables import logPath

def masterLogging():
    _loggerConfig = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },  
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': logPath+'/master.log',
                'maxBytes': 16777216,
                'backupCount': 20,
                'encoding': 'utf8'
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True
            },
        }
    }
    logging.config.dictConfig(_loggerConfig)