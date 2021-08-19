import requests
import time

DELAY_MINUTES = 20

def keepalive(logger):
    logger.debug("running...")
    while True:
        r = requests.get('https://pets-io.herokuapp.com/')
        logger.debug("request : {}".format(r.status_code))
        time.sleep(DELAY_MINUTES * 60)