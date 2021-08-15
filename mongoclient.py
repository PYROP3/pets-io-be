from pymongo import MongoClient
from bson.objectid import ObjectId
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

    def invalidate(self, fcm_token):
        self.client.sessions.find_one_and_delete({c.FCM_TOKEN_KEY: fcm_token})

    def session(self, user, password, fcm_token):
        __pass = utils.hash_password(user, password)
        __auth = self.client.users.find_one({
            c.USER_EMAIL_KEY: user,
            c.USER_PASS_KEY: __pass
        })
        if __auth is None:
            self.logger.debug('Invalid credentials found')
            return None

        __auth = self.client.sessions.find_one({c.USER_EMAIL_KEY: user, c.FCM_TOKEN_KEY: fcm_token}, {c.USER_TOKEN_KEY: 1, "_id": 0})
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

    def session_to_user(self, session):
        __auth = self.client.sessions.find_one({c.USER_TOKEN_KEY: session}, {c.USER_EMAIL_KEY: 1, "_id": 0})
        if __auth is not None:
            return __auth[c.USER_EMAIL_KEY]
        return None

    def logout(self, token, fcm_token):
        __auth = self.client.sessions.find_one_and_delete({c.USER_TOKEN_KEY: token, c.FCM_TOKEN_KEY: fcm_token})
        if __auth is None:
            self.logger.debug('No such session')

    def event(self, time, device_id, pet, image, event_extra):
        # Find owner of device
        __user = self.get_device_owner(device_id)
        self.logger.debug('Found user {} owner of {}'.format(__user, device_id))

        self.client.events.insert_one({
            c.DEVICE_ID_KEY: device_id,
            c.USER_EMAIL_KEY: __user,
            c.USER_TIMESTAMP_KEY: time,
            c.EVENT_PICTURE_KEY: image,
            c.EVENT_PET_KEY: pet,
            c.EVENT_EXTRA_KEY: event_extra
        })

        return __user

    def get_fcm_ids(self, user):
        __fcm_ids = []
        if user is not None:
            for __fcm_query in self.client.sessions.find({c.USER_EMAIL_KEY: user}, {c.FCM_TOKEN_KEY: 1, "_id": 0}):
                __fcm_ids += [__fcm_query[c.FCM_TOKEN_KEY]]
        return __fcm_ids

    def get_device_ids(self, user):
        __device_ids = []
        if user is not None:
            for __dev_query in self.client.devices.find({c.USER_EMAIL_KEY: user}, {c.DEVICE_ID_KEY: 1, "_id": 0}):
                __device_ids += [__dev_query[c.DEVICE_ID_KEY]]
        return __device_ids

    def get_device_owner(self, device):
        if device is not None:
            return self.client.devices.find_one({c.DEVICE_ID_KEY: device}, {c.USER_EMAIL_KEY: 1, "_id": 0})[c.USER_EMAIL_KEY]
        return None

    def get_events_for_device(self, device):
        if device is not None:
            __owner = self.get_device_owner(device)
            return list(self.client.events.find({c.DEVICE_ID_KEY: device, c.USER_EMAIL_KEY: __owner}))
        return []

    def get_event_by_id(self, event_id):
        if event_id is not None:
            return self.client.events.find_one({"_id":ObjectId(event_id)})
        return None

    def get_pets(self, user):
        if user is not None:
            __pets = self.client.pets.find({c.PET_OWNER_KEY: user})
            if __pets is not None:
                return [pet for pet in __pets]
        return []

    def get_pet(self, pet, user):
        if user is not None and pet is not None:
            return self.client.pets.find_one({c.PET_OWNER_KEY: user, "_id":ObjectId(pet)})
        return None
