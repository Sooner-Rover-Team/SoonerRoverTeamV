import socket
import configparser
import util
import os

# UNFINISHED

if os.path.dirname(__file__) != '':
    current_folder = os.path.dirname(__file__)
    os.chdir(current_folder)


# Get the IP address of the server
config = configparser.ConfigParser()
config.read('./config.ini')
USING_BRIDGE = config.getboolean('Connection', 'USING_BRIDGE')
BRIDGE_HOST = config['Connection']['BRIDGE_HOST'] # is this the base station ip ?
EBOX_HOST = config['Connection']['EBOX_HOST']
EBOX_PORT = int(config['Connection']['EBOX_PORT'])
ARM_HOST = config['Connection']['ARM_HOST']
ARM_PORT = int(config['Connection']['ARM_PORT'])
SCI_HOST = config['Connection']['SCI_HOST']
SCI_PORT = int(config['Connection']['SCI_PORT'])
CONT_CONFIG = int(config['Controller']['CONFIG'])
