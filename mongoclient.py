from pymongo import MongoClient
from constants import constants
from dotenv import load_dotenv
from os import environ as env
import utils
import string
import random
from datetime import datetime

load_dotenv()
c = constants()

class mongo_helper:

    def __init__(self, logger):
        #self.__url = "mongodb+srv://"+env["MONGO_USER"]+":"+env["MONGO_PASS"]+"@"+env["MONGO_URL"]+"/"+env["MONGO_DB_NAME"]+"?retryWrites=true&w=majority"
        self.__url = "mongodb+srv://{}:{}@{}/{}?retryWrites=true&w=majority".format(env["MONGO_USER"], env["MONGO_PASS"], env["MONGO_URL"], env["MONGO_DB_NAME"])
        self.__db = MongoClient(self.__url)
        self.client = self.__db.UserData
        self.logger = logger

    def session(self, user, password, fcm_token):
        __pass = utils.hash_password(user, password)
        __auth = self.client.users.find_one({
            c.USER_EMAIL_KEY: user,
            c.USER_PASS_KEY: __pass
        })
        if __auth is None:
            self.logger.debug('Invalid credentials found')
            return None

        __auth = self.client.sessions.find_one({c.USER_EMAIL_KEY: user, c.FCM_TOKEN_KEY: fcm_token})
        if __auth is not None:
            self.logger.debug('Active session found')
            return __auth[c.USER_TOKEN_KEY]

        __token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(c.AUTH_TOKEN_LENGTH))
        self.client.sessions.insert_one({
            c.USER_EMAIL_KEY: user,
            c.USER_TOKEN_KEY: __token,
            c.USER_TIMESTAMP_KEY: datetime.utcnow(),
            c.FCM_TOKEN_KEY: fcm_token
        })

        return __token

    def logout(self, token, fcm_token):
        __auth = self.client.sessions.find_one_and_delete({c.USER_TOKEN_KEY: token, c.FCM_TOKEN_KEY: fcm_token})
        if __auth is None:
            self.logger.debug('No such session')
