import firebase_admin
from firebase_admin import messaging
from dotenv import load_dotenv
from os import environ as env
from constants import constants
import utils

load_dotenv()
c = constants()

cred = firebase_admin.credentials.Certificate({
  "type": "service_account",
  "project_id": "pets-io-tcc",
  "private_key_id": env["FIREBASE_KEY_ID"],
  "private_key": env["FIREBASE_KEY"].replace("\\n", "\n"),
  "client_email": env["FIREBASE_EMAIL"],
  "client_id": env["FIREBASE_ID"],
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": env["FIREBASE_CERT_URL"]
})
__app = firebase_admin.initialize_app(cred)

def send_to_token(fcm_token, data):
    # [START send_to_token]

    # See documentation on defining a message payload.
    message = messaging.Message(
        data=data,
        token=fcm_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    return messaging.send(message)
    # [END send_to_token]

def event_to_message(device_id, event_extra):
    __device_type = utils.get_device_type(device_id)
    return {
        c.DEVICE_TYPE_KEY: __device_type,
        c.EVENT_EXTRA_KEY: event_extra
    }