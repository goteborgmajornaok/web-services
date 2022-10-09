#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-
try:
    import os
    import logging
    from logging.handlers import RotatingFileHandler
    import datetime
    from pathlib import Path

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    log_dir = ROOT_DIR + '/logs/'

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(filename=log_dir + '/app.log', maxBytes=200 * 1024 * 1024, backupCount=1,
                                  encoding='UTF-8')
    formatter = logging.Formatter(
        '%(asctime)s,%(msecs)d, LEVEL: %(levelname)s, FILE: %(filename)s, FUNCTION: %(funcName)s, LINE: %(lineno)d, %(message)s',
        '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    from wsgiref.handlers import CGIHandler
    from application.main import flaskapp

    CGIHandler().run(flaskapp)
except (ModuleNotFoundError, ImportError) as e:
    import subprocess
    import sys

    for l in open(ROOT_DIR + '/requirements.txt'):
        logging.info(f'Installing {l.rstrip()}')
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", l.rstrip()])
        except Exception as e:
            logging.error(e)

    print("Content-Type: text/html")
    print()
    print("<h1>Environment has been reset. Try reloading page.</h1>")
except Exception as e:
    logging.error(e)
    print("Content-Type: text/html")
    print()
    print("<h1>Unhandled error</h1>")
    print("<p>Check log files.</p>")
