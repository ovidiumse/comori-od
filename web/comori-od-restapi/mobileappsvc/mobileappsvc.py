import os
import jwt
from datetime import datetime, timedelta
from api_utils import timeit
import logging

LOGGER_ = logging.getLogger(__name__)

class MobileAppService(object):
    auth = {
        'auth_disabled': True
    }

    def __init__(self):
        self.public_key_ecdsa = os.environ.get("MOBILE_APP_PKEY_ECDSA")
    
    @timeit("Authorizing", __name__)
    def authorize(self, authorization):
        return jwt.decode(authorization, self.public_key_ecdsa, algorithms='ES512', options={"verify_exp": True}, leeway=timedelta(seconds=10))

    def getUserId(self, auth):
        return "{}.{}".format(auth['sub'], auth['iss'])

    def getDocumentId(self, auth, id):
        return "{}.{}".format(self.getUserId(auth), id)

    def fmtUtcNow(self):
        return f"{datetime.utcnow().isoformat()}Z"