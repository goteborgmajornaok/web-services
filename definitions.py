import configparser
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = 'config.cfg'

config = configparser.ConfigParser()
config.read(CONFIG, encoding='utf8')
