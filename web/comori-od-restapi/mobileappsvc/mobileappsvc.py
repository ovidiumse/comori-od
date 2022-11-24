import os
import jwt
from datetime import datetime
from api_utils import timeit
import logging
import pytz
from calendar import timegm

LOGGER_ = logging.getLogger(__name__)

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
            auth = jwt.decode(authorization, self.public_key_ecdsa, algorithms='ES512', options={"verify_exp": True})
            LOGGER_.info(f"JWT: {auth}\niat: {datetime.fromtimestamp(auth['iat'])}\nexp: {datetime.fromtimestamp(auth['exp'])}\nutc: {datetime.now(pytz.utc)} or {timegm(datetime.now(tz=pytz.utc).utctimetuple())}")
            return auth
        except jwt.exceptions.InvalidAlgorithmError:
            LOGGER_.warn("Using RS256 JWT key!")
            return jwt.decode(authorization, self.public_key, algorithms='RS256', options={"verify_exp": True})

    def getUserId(self, auth):
        return "{}.{}".format(auth['sub'], auth['iss'])

    def getDocumentId(self, auth, id):
        return "{}.{}".format(self.getUserId(auth), id)

    def fmtUtcNow(self):
        return f"{datetime.utcnow().isoformat()}Z"