from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

import logging
logger = logging.getLogger('xadmins')
logging.basicConfig(filename='xadmins/test.log', level=logging.INFO,
                    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        global user
        try:
            user = User.objects.get(email=username)
        except Exception as e:
            return None
        else:
            if user.check_password(password):
                return user
        return None





