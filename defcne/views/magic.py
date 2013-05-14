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

    def event(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['shortname'] = event.shortname
        e['description'] = event.description
        e['website'] = event.website
        e['logo'] = self.request.registry.settings['defcne.upload_path'] + event.logo if event.logo else ''
        e['hrsofoperation'] = event.hrsofoperation
        e['tables'] = event.tables
        e['chairs'] = event.chairs
        e['represent'] = event.represent
        e['numparticipants'] = event.numparticipants
        e['blackbadge'] = event.blackbadge
        e['status'] = status_types[event.status]

        e['pocs'] = [x.name for x in event.pocs]
        e['power'] = [{'amps': x.amps, 'outlets': x.outlets, 'justification': x.justification} for x in event.power]
        e['drops'] = [{'typeof': x.typeof, 'justification': x.justification} for x in event.drops]
        e['aps'] = [{'hwmac': x.hwmac, 'apbrand': x.apbrand, 'ssid': x.ssid} for x in event.aps]
        e['owner'] = [x.disp_uname for x in event.owner]
        e['ticket_count'] = len(m.Ticket.find_event_tickets(event.id))
        e['tickets'] = m.Ticket.find_event_tickets(event.id)

        e['edit_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname, 'edit'))
        e['manage_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname, 'manage'))
        e['magic_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname))

        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.resource_url(self.context, 'extrainfo'), buttons=('submit',))

        return {
                'page_title': '{}'.format(event.disp_name),
                'event': e,
                'form': f.render()
                }


    def users(self):
        return {}

    def user(self):
        return {}

