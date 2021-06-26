import hashlib
import re
from constants import constants as c

def hash_password(user, password):
    return hashlib.sha256("{}.{}".format(user, password).encode('utf-8')).hexdigest()

def parse_token(token):
    if token is None:
        return None

    if token.find(c.AUTH_TOKEN_NAME) != 0:
        return None

    __token = token[len(c.AUTH_TOKEN_NAME):]

    if len(__token) != c.AUTH_TOKEN_LENGTH:
        return None
    
    return __token

def get_device_type(device_id):
    __prog = re.compile(c.DEVICE_ID_FORMAT)
    __match = __prog.match(device_id)
    if __match is None:
        return None
    __dev_type = __match.groups()[0]
    if __dev_type not in c.DEVICE_TYPE_DICT:
        return None
    return c.DEVICE_TYPE_DICT[__dev_type]