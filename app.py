#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-
try:
    import os
    import logging

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    logging.basicConfig(filename=ROOT_DIR + '/app.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
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
