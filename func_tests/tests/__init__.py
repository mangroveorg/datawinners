# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging

logging.getLogger('selenium.webdriver.firefox').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.chrome').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.remote').setLevel(logging.ERROR)
logging.getLogger('webdriver.ExtensionConnection').setLevel(logging.ERROR)