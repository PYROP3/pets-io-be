from firebase_admin import messaging
from constants import constants as c
import utils

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