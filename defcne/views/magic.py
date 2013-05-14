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
        return HTTPSeeOther(location=self.request.route_url('defcne.magic', traverse=('e', '21')))

    def dcevents(self):
        all_events = m.DBSession.query(m.Event).filter(m.Event.dc == self.context.__name__).order_by(m.Event.name.asc()).all()

        events = []
        for event in all_events:
            e = {}
            e['name'] = event.disp_name
            e['owner'] = [x.disp_uname for x in event.owner]
            e['status'] = status_types[event.status]
            e['blackbadge'] = event.blackbadge
            e['edit_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname, 'edit'))
            e['manage_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname, 'manage'))
            e['magic_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname))
            events.append(e)

        print events

        return {
                'page_title': 'All Events',
                'events': events,
                }


    def users(self):
        return {}

    def user(self):
        return {}

