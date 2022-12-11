import time
import jwt
from decouple import config
from datetime import datetime


JWT_SECRET = config('secret')
JWT_ALGORITHM = config('alg')


def token_response(token: str):
    return {
        "access_token": token
    }


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        bad = "expired"
        return decoded_token if decoded_token["expires"] >= time.mktime(datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), "%Y-%m-%d %H:%M:%S.%f").timetuple()) else bad
        
    except:
        return {}
