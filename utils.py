import hashlib
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