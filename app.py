#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
import logging


logging.basicConfig(filename='myapp.log', level=logging.INFO)

try:
    from wsgiref.handlers import CGIHandler
    from application.main import flaskapp

    CGIHandler().run(flaskapp)
except (ModuleNotFoundError, ImportError) as e:
    import subprocess
    import sys
    from definitions import ROOT_DIR

    for l in open(ROOT_DIR + f'/requirements.txt'):
        subprocess.check_call([sys.executable, "-m", "pip", "install", l.rstrip()])

    print("Content-Type: text/html")
    print()
    print("<h1>Environment has been reset. Try reloading page.</h1>")

