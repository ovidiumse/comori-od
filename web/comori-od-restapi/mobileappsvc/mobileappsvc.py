import os
import jwt
from datetime import datetime
from api_utils import timeit

class MobileAppService(object):
    auth = {
        'auth_disabled': True
    }

    def __init__(self):
        self.public_key = os.environ.get("MOBILE_APP_PKEY")
        self.public_key_ecdsa = os.environ.get("MOBILE_APP_PKEY_ECDSA")
    
    @timeit("Authorizing", __name__)
    def authorize(self, authorization):
        try:
            return jwt.decode(authorization, self.public_key_ecdsa, algorithms='ES512')
        except jwt.exceptions.InvalidAlgorithmError:
            return jwt.decode(authorization, self.public_key, algorithms='RS256')

    def getUserId(self, auth):
        return "{}.{}".format(auth['sub'], auth['iss'])

    def getDocumentId(self, auth, id):
        return "{}.{}".format(self.getUserId(auth), id)

    def fmtUtcNow(self):
        return f"{datetime.utcnow().isoformat()}Z"