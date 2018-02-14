import logging
import os
import sys


def configure_log():

    log = logging.getLogger('hubspot3')
    log.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(os.path.join(
        os.path.dirname(__file__), 'test_run.log'), mode='w')
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)-5s %(name)s === %(message)s')
    file_handler.setFormatter(formatter)

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-5s %(name)s === %(message)s', datefmt='%M:%S')
    console_handler.setFormatter(formatter)

    log.addHandler(file_handler)
    log.addHandler(console_handler)

    return log


configure_log()
