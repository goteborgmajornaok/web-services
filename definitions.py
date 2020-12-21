import configparser
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = 'config.cfg'

config = configparser.ConfigParser()
config.read(CONFIG, encoding='utf8')

TMP_CONFIG = 'tmp.cfg'
tmp_config = configparser.ConfigParser()
tmp_config.read(TMP_CONFIG, encoding='utf8')


def write_tmp():
    with open('tmp.cfg', 'w') as f:
        tmp_config.write(f)
    tmp_config.read(TMP_CONFIG, encoding='utf8')
