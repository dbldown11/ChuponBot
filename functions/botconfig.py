# IMPORT THE CONFIGPARSER MODULE AND PLATFORM MODULE
import configparser
import platform

# my machine is Windows so if it's on my machine, it's dev, if it's on a real host, it's production
if "Windows" in platform.platform():
    env = "dev"
else:
    env = "prod"

config = configparser.ConfigParser()
config.read('config.ini')
