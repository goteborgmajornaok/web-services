import configparser
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = ROOT_DIR + '\\config.cfg'


def get_config():
    config = configparser.ConfigParser()
    config.read(CONFIG, encoding='utf8')
    return config
