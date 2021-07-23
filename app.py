from constants import constants
from datetime import datetime
from dotenv import load_dotenv
from emails import email_sender
from flask import Flask, request, abort, render_template
from mongoclient import mongo_helper
from types import MethodType
from bson.binary import Binary

import base64
import notifications
import random
import string
import utils
import json

load_dotenv()

c = constants()
email = email_sender()

app = Flask(__name__)
app.logger.root.setLevel(0)

mongo = mongo_helper(app.logger)
db = mongo.client

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
    
@app.route(c.CREATE_ACCOUNT_REQUEST, methods=['POST'])
def post_req_create_account():
    app.logger.debug(post_req_create_account.__name__)

    __form = request.get_json()

    __email = __form[c.USER_EMAIL_KEY]
    
    __db = db.users.find_one({
        c.USER_EMAIL_KEY: __email
    })

    if (__db is not None):
        app.logger.debug('Account for {} already exists'.format(__email))
        abort(400)
    
    __token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))

    __user = {
        c.USER_EMAIL_KEY: __email,
        c.USER_PASS_KEY: utils.hash_password(__email, __form[c.USER_PASS_KEY]),
        c.USER_NAME_KEY: __form[c.USER_NAME_KEY],
        c.USER_N_PETS_KEY: int(__form[c.USER_N_PETS_KEY]),
        c.USER_TOKEN_KEY: __token
    }
    db.pending_users.insert_one(__user)

    __email_content = render_template(
        'validation.html',
        mainURL=c.SERVER_URL_DEFAULT,
        name=__user[c.USER_NAME_KEY],
        authToken=__token
    )

    email.send(
        __email, 
        __email_content
    )

    return c.SUCCESS_MSG

@app.route(c.VERIFY_ACCOUNT_REQUEST)
def get_req_verify_account():
    app.logger.debug(get_req_verify_account.__name__)
    
    __token = request.args.get(c.USER_TOKEN_KEY)
    if __token is None:
        app.logger.debug('No token')
        abort(401)

    __auth = db.pending_users.find_one_and_delete({c.USER_TOKEN_KEY: __token})
    if __auth is None:
        app.logger.debug('No such pending user found')
        abort(401)
    
    __db = db.users.find_one({
        c.USER_EMAIL_KEY: __auth[c.USER_EMAIL_KEY]
    })

    if (__db is not None):
        app.logger.debug('Account for {} already exists'.format(__auth[c.USER_EMAIL_KEY]))
        abort(401)

    app.logger.debug('Validated user ' + str(__auth))

    __user = {
        c.USER_EMAIL_KEY: __auth[c.USER_EMAIL_KEY],
        c.USER_PASS_KEY: __auth[c.USER_PASS_KEY],
        c.USER_NAME_KEY: __auth[c.USER_NAME_KEY],
        c.USER_N_PETS_KEY: -1 * __auth[c.USER_N_PETS_KEY],
        c.USER_PENDING_PETS_KEY: __auth[c.USER_N_PETS_KEY],
        c.USER_N_DEVICES_KEY: 0,
    }

    db.users.insert_one(__user)

    return c.SUCCESS_MSG

@app.route(c.AUTH_REQUEST, methods=['POST'])
def post_req_auth():
    app.logger.debug(post_req_auth.__name__)
    app.logger.debug(request.get_json())

    __form = request.get_json()

    __email = __form[c.USER_EMAIL_KEY]
    __pass = __form[c.USER_PASS_KEY]
    __fcm = __form[c.FCM_TOKEN_KEY]
    
    __auth = mongo.session(__email, __pass, __fcm)
    if __auth is None:
        app.logger.debug('Could not auth ' + __email)
        abort(401)

    __user = db.users.find_one({c.USER_EMAIL_KEY: __email}, {c.USER_PASS_KEY: 0, "_id": 0})
    app.logger.debug('Authenticated user ' + str(__user))
    __user[c.USER_TOKEN_KEY] = __auth

    return __user
    
@app.route(c.DEAUTH_REQUEST)
def get_req_deauth():
    app.logger.debug(get_req_deauth.__name__)

    __auth = utils.parse_token(request.headers.get('Authorization'))
    app.logger.debug('Deauth : {}'.format(__auth))

    if __auth is None:
        abort(401)
    
    __token = request.args.get(c.USER_TOKEN_KEY)

    mongo.logout(__auth, __token)

    return c.SUCCESS_MSG

@app.route(c.EVENT_TRIGGERED_REQUEST, methods=['POST'])
def post_req_event_triggered():
    app.logger.debug(post_req_event_triggered.__name__)
    app.logger.debug(request.get_data())

    __form = json.loads(request.get_data())
    __now = datetime.utcnow()
    __device_id = __form[c.DEVICE_ID_KEY]
    __img_bytes = base64.b64decode(__form['Img'])
    __event_extra = None if __form['Extra'] == "null" else __form['Extra']

    # TODO detect pet with AI
    __pet = None
    __user = mongo.event(__now, __device_id, __pet, __img_bytes, __event_extra)

    if __user is not None:
        for __fcm_id in mongo.get_fcm_ids(__user):
            notifications.send_to_token(__fcm_id, notifications.event_to_message(__device_id, __event_extra))
    else:
        app.logger.warn('Device {} triggered event but has no registered user'.format(__device_id))
        abort(401)

    return c.SUCCESS_MSG

@app.route(c.REGISTER_DEVICE_REQUEST, methods=['POST'])
def post_req_register_device():
    app.logger.debug(post_req_register_device.__name__)

    __auth = utils.parse_token(request.headers.get('Authorization'))
    app.logger.debug('Register device : {}'.format(__auth))
    
    __db = db.sessions.find_one({
        c.USER_TOKEN_KEY: __auth
    }, {c.USER_EMAIL_KEY: 1})

    if (__db is None):
        app.logger.debug('Could not find user for session')
        abort(401)

    # __token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
    __token = "A1B2C3" # FIXME TEST ONLY

    db.pending_devices.insert_one({
        c.USER_EMAIL_KEY: __db[c.USER_EMAIL_KEY],
        c.REQUEST_TOKEN_KEY: __token
    })
    
    return __token

@app.route(c.CONFIRM_DEVICE_REQUEST, methods=['POST'])
def post_req_confirm_device():
    app.logger.debug(post_req_confirm_device.__name__)
    app.logger.debug(request.get_data())

    __form = json.loads(request.get_data())
    __device_id = __form[c.DEVICE_ID_KEY]
    __request_id = __form[c.REQUEST_TOKEN_KEY]

    __req = db.pending_devices.find_one_and_delete({
        c.REQUEST_TOKEN_KEY: __request_id
    })

    if __req is None:
        app.logger.debug('Could not find device request')
        abort(400)

    db.devices.insert_one({
        c.USER_EMAIL_KEY: __req[c.USER_EMAIL_KEY],
        c.DEVICE_ID_KEY: __device_id
    })

    app.logger.debug('Registered device {} to user {}'.format(__device_id, __req[c.USER_EMAIL_KEY]))
    
    return c.SUCCESS_MSG
