# File: magic.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-04-01

import logging
log = logging.getLogger(__name__)

from uuid import uuid4

from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPSeeOther, HTTPNotFound

import transaction

from sqlalchemy.exc import IntegrityError
from deform import (Form, ValidationFailure)

#from ..forms import (
#        )

from .. import models as m

class Magic(object):
    """View for Magic functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def main(self):
        return {
                'page_title': 'Magic Portal',
                }

    def dcyears(self):
        return {}

    def dcevents(self):
        return {}

    def users(self):
        return {}

    def user(self):
        return {}

