#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-
from definitions import ROOT_DIR
import logging

logging.basicConfig(filename=ROOT_DIR + '/app.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

try:
    from wsgiref.handlers import CGIHandler
    from application.main import flaskapp

    CGIHandler().run(flaskapp)
except (ModuleNotFoundError, ImportError) as e:
    import subprocess
    import sys

    for l in open(ROOT_DIR + f'/requirements.txt'):
        subprocess.check_call([sys.executable, "-m", "pip", "install", l.rstrip()])

    print("Content-Type: text/html")
    print()
    print("<h1>Environment has been reset. Try reloading page.</h1>")
except Exception as e:
    logging.error(e)
    raise e
