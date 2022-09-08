import configparser
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = ROOT_DIR + '/config.cfg'

config = configparser.ConfigParser()
config.read(CONFIG, encoding='utf8')

TMP_CONFIG = ROOT_DIR + '/tmp.cfg'
tmp_config = configparser.ConfigParser()
tmp_config.read(TMP_CONFIG, encoding='utf8')


def write_tmp():
    with open(ROOT_DIR + '/tmp.cfg', 'w') as f:
        tmp_config.write(f)
    tmp_config.read(TMP_CONFIG, encoding='utf8')
