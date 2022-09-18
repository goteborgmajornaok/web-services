#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-
try:
    import os
    import logging
    import datetime
    from pathlib import Path

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    log_dir = ROOT_DIR + '/logs/' + datetime.date.today().strftime("%Y/%m")

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(filename=log_dir + '/' + datetime.date.today().strftime("%d") + '.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d, LEVEL: %(levelname)s, FILE: %(filename)s, FUNCTION: %(funcName)s, LINE: %(lineno)d, %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

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
