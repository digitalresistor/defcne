# File: event.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-03-03


import os
import os.path
import shutil

import logging
log = logging.getLogger(__name__)
import string

from uuid import uuid4

from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPSeeOther, HTTPInternalServerError, HTTPNotFound
from pyramid.renderers import render_to_response

import transaction

from sqlalchemy.exc import IntegrityError
from deform import (Form, ValidationFailure)

from ..forms import (
        EventForm,
        )

#from ..forms.Event import (
#        )

from .. import models as m


class Event(object):
    """View for Event functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create(self):
        if 'letsgo' in self.request.subpath:
            schema = EventForm().bind(request=self.request)
            f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
            return {
                    'form': f.render(),
                    'page_title': 'Create Contest or Event',
                    'explanation': None,
                    }
        else:
            return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse='guidelines'))

    def create_submit(self):
        controls = self.request.POST.items()
        schema = EventForm().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = f.validate(controls)

            if appstruct['logo'] is not None:
                logo_path = '/' + string.replace(str(uuid4()), '-', '/') + os.path.splitext(appstruct['logo']['filename'])[1]
                logo_save = self.request.registry.settings['defcne.upload_path'] + logo_path
                logo_save_path = os.path.dirname(logo_save)

                try:
                    os.makedirs(logo_save_path)
                except:
                    raise HTTPInternalServerError()

                with open(logo_save, 'w+b') as f:
                    appstruct['logo']['fp'].seek(0)
                    shutil.copyfileobj(appstruct['logo']['fp'], f)
            else:
                logo_path = None

            event = m.Event(
                    name=appstruct['name'],
                    shortname=appstruct['shortname'],
                    description=appstruct['description'],
                    website=appstruct['website'],
                    logo=logo_path,
                    hrsofoperation=appstruct['hrsoperation'],
                    tables=appstruct['tables'],
                    chairs=appstruct['chairs'],
                    represent=appstruct['represent'],
                    numparticipants=appstruct['numparticipants'],
                    )

            for power in appstruct['power']:
                event.power.append(m.EventPower(amps=power['amps'], outlets=power['outlets'], justification=power['justify']))

            for poc in appstruct['pocs']:
                event.pocs.append(m.EventPOC(name=poc['name'], email=poc['email'], cellphone=poc['cellphone']))

            for drop in appstruct['wiredaccess']:
                event.drops.append(m.EventWiredDrop(typeof=drop['typeof'], justification=drop['justify']))

            for ap in appstruct['wirelessap']:
                event.aps.append(m.EventAP(hwmac=ap['hwmac'], apbrand=ap['apbrand'], ssid=ap['ssid']))

            event.owner.append(self.request.user.user)
            event.dc = 21;

            m.DBSession.add(event)
            m.DBSession.flush()

            return {}
        except ValidationFailure, e:
            return {
                'form': e.render(),
                'page_title': 'Create Contest or Event',
                'explanation': None,
                }

    def create_not_authed(self):
        if 'letsgo' in self.request.subpath:
            return {}
        else:
            return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse='guidelines'))

    def guidelines(self):
        return {}

    def main(self):
        return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse='21'))

    def defcon(self):
        dc = m.Defcon.find_defcon_events(self.context.__name__)

        if dc is None:
            raise HTTPNotFound()

        events = []

        for event in dc.events:
            if event.status != 5:
                continue
            e = {}
            e['name'] = event.name
            e['description'] = event.description
            e['website'] = event.website
            e['owner'] = [x.disp_uname for x in event.owner]
            events.append(e)

        return {
                'events': events,
                'page_title': 'DEFCON {0}'.format(self.context.__name__),
                }

    def event(self):
        print self.context.__name__
        return {}

