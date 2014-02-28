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

from pyramid.view import (
        view_config,
        view_defaults,
        )
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import (
        HTTPSeeOther,
        HTTPInternalServerError,
        HTTPNotFound,
        HTTPForbidden,
        )
from pyramid.renderers import render_to_response

import transaction

from sqlalchemy.exc import IntegrityError
from deform import (Form, ValidationFailure)

from ..forms import (
        EventForm,
        TicketForm,
        )

from ..events import (
        ContestEventCreated,
        ContestEventUpdated,
        ContestEventTicketUpdated,
        )

from .. import models as m
from ..models.event import status_types

@view_defaults(route_name='defcne.e')
class Event(object):
    """View for Event functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(context='..acl.EventCreate', renderer='event/form.mako', permission='create')
    @view_config(context='..acl.EventCreate', renderer='event/form.mako', permission='create', name='letsgo')
    def create(self):
        if 'letsgo' == self.request.path.split('/')[-1]:
            schema = EventForm().bind(request=self.request)
            f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
            return {
                    'form': f.render(),
                    'page_title': 'Create Contest or Event',
                    'explanation': None,
                    }
        else:
            return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse='guidelines'))


    @view_config(context='..acl.EventCreate', name='letsgo', renderer='event/form.mako', permission='create', request_method='POST')
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

            if len(appstruct['otherrequests']['ticket']) != 0:
                ticket = m.Ticket(ticket=appstruct['otherrequests']['ticket'], user=self.request.user.user)
                event.tickets.append(ticket)

            m.DBSession.add(event)
            m.DBSession.flush()

            self.request.registry.notify(ContestEventCreated(self.request, self.context, event))
            self.request.session.flash('Your contest or event has been created. The staff has been notified!', queue='event')
            return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'manage')))
        except ValidationFailure, e:
            return {
                'form': e.render(),
                'page_title': 'Create Contest or Event',
                'explanation': None,
                }
    @view_config(context=HTTPForbidden, containment='..acl.EventCreate', renderer='event/accountneeded.mako')
    def create_not_authed(self):
        if 'letsgo' == self.request.path.split('/')[-1]:
            return {}
        else:
            return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse='guidelines'))

    # If the user attempts to access a page that requires authorization, but
    # they are not logged in, instead of sending them to the login page, we
    # simply send them a not found page. Maybe not as nice for the user if they
    # thought they were logged in, but at least management URL's don't get
    # "advertised" with a "please login =)"
    @view_config(context=HTTPForbidden, containment='..acl.Event', renderer='not_found.mako')
    def not_authed(self):
        self.request.status_int = 404
        return {}

    @view_config(name='guidelines', renderer='event/rules.mako')
    def guidelines(self):
        return {}

    @view_config(context='..acl.Events')
    def main(self):
        return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse='21'))

    @view_config(context='..acl.DefconEvent', renderer='event/all.mako')
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
            e['url'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname))
            events.append(e)

        return {
                'events': events,
                'page_title': 'DEF CON {0} Contests/Events'.format(self.context.__name__),
                }

    @view_config(context='..acl.Event', renderer='event/one.mako', permission='view')
    def event(self):
        event = self.context.event
        e = {}
        e['name'] = event.name
        e['description'] = event.description
        e['website'] = event.website
        e['owner'] = [x.disp_uname for x in event.owner]
        e['url'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname))

        return {
                'page_title': '{}'.format(event.disp_name),
                'event': e,
                }

    @view_config(context='..acl.Event', name='edit', renderer='event/edit.mako', permission='edit')
    def edit(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'extrainfo'))

        astruct = {}
        astruct['website'] = event.website
        astruct['hrsoperation'] = event.hrsofoperation
        astruct['represent'] = event.represent
        astruct['name'] = event.disp_name
        astruct['shortname'] = event.shortname
        astruct['description'] = event.description
        astruct['numparticipants'] = event.numparticipants
        astruct['tables'] = event.tables
        astruct['chairs'] = event.chairs
        astruct['power'] = [{'id': p.id, 'outlets': p.outlets, 'amps': p.amps, 'justify': p.justification} for p in event.power]
        astruct['pocs'] = [{'id': p.id, 'email': p.email, 'cellphone': p.cellphone, 'name': p.name} for p in event.pocs]
        astruct['wiredaccess'] = [{'id': w.id, 'justify': w.justification, 'typeof': w.typeof} for w in event.drops]
        astruct['wirelessap'] = [{'id': w.id, 'ssid': w.ssid, 'apbrand': w.apbrand, 'hwmac': w.hwmac} for w in event.aps]

        schema = EventForm().bind(request=self.request)
        if event.logo:
            schema['logo'].description = "A logo has already been uploaded. Uploading a new logo will overwrite the previous logo!"
        del schema['otherrequests']

        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        return {
                'page_title': 'Edit contest/event: {}'.format(event.disp_name),
                'event': e,
                'form': f.render(astruct),
                }

    @view_config(context='..acl.Event', name='edit', renderer='event/edit.mako', permission='edit', request_method='POST')
    def edit_submit(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'extrainfo'))

        controls = self.request.POST.items()
        schema = EventForm().bind(request=self.request, eventname=event.disp_name, shortname=event.shortname)
        del schema['otherrequests']
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

            event.name=appstruct['name']
            event.shortname=appstruct['shortname']
            event.description=appstruct['description']
            event.website=appstruct['website']
            if logo_path is not None:
                event.logo=logo_path
            event.hrsofoperation=appstruct['hrsoperation']
            event.tables=appstruct['tables']
            event.chairs=appstruct['chairs']
            event.represent=appstruct['represent']
            event.numparticipants=appstruct['numparticipants']

            new_power_ids = set([p['id'] for p in appstruct['power'] if p['id'] != -1])
            cur_power_ids = set([p.id for p in event.power])
            del_power_ids = cur_power_ids - new_power_ids

            if len(del_power_ids):
                for power in event.power:
                    if power.id in del_power_ids:
                        m.DBSession.delete(power)

            for power in appstruct['power']:
                if power['id'] in cur_power_ids:
                    cur_power = [p for p in event.power if p.id == power['id']][0]
                    cur_power.amps = power['amps']
                    cur_power.outlets = power['outlets']
                    cur_power.justification = power['justify']
                else:
                    event.power.append(m.EventPower(amps=power['amps'], outlets=power['outlets'], justification=power['justify']))

            new_poc_ids = set([p['id'] for p in appstruct['pocs'] if p['id'] != -1])
            cur_poc_ids = set([p.id for p in event.pocs])
            del_poc_ids = cur_poc_ids - new_poc_ids

            if len(del_poc_ids):
                for poc in event.pocs:
                    if poc.id in del_poc_ids:
                        m.DBSession.delete(poc)

            for poc in appstruct['pocs']:
                if poc['id'] in cur_poc_ids:
                    cur_poc = [p for p in event.pocs if p.id == poc['id']][0]
                    cur_poc.name = poc['name']
                    cur_poc.email = poc['email']
                    cur_poc.cellphone = poc['cellphone']
                else:
                    event.pocs.append(m.EventPOC(name=poc['name'], email=poc['email'], cellphone=poc['cellphone']))

            new_drop_ids = set([d['id'] for d in appstruct['wiredaccess'] if d['id'] != -1])
            cur_drop_ids = set([d.id for d in event.drops])
            del_drop_ids = cur_drop_ids - new_drop_ids

            if len(del_drop_ids):
                for drop in event.drops:
                    if drop.id in del_drop_ids:
                        m.DBSession.delete(drop)

            for drop in appstruct['wiredaccess']:
                if drop['id'] in cur_drop_ids:
                    cur_drop = [d for d in event.drops if d.id == drop['id']][0]
                    cur_drop.typeof = drop['typeof']
                    cur_drop.justification = drop['justify']
                else:
                    event.drops.append(m.EventWiredDrop(typeof=drop['typeof'], justification=drop['justify']))

            new_ap_ids = set([a['id'] for a in appstruct['wirelessap'] if a['id'] != -1])
            cur_ap_ids = set([a.id for a in event.aps])
            del_ap_ids = cur_ap_ids - new_ap_ids

            if len(del_ap_ids):
                for ap in event.aps:
                    if ap.id in del_ap_ids:
                        m.DBSession.delete(ap)

            for ap in appstruct['wirelessap']:
                if ap['id'] in cur_ap_ids:
                    cur_ap = [a for a in event.aps if a.id == ap['id']][0]
                    cur_ap.hwmac = ap['hwmac']
                    cur_ap.apbrand = ap['apbrand']
                    cur_ap.ssid = ap['ssid']
                else:
                    event.aps.append(m.EventAP(hwmac=ap['hwmac'], apbrand=ap['apbrand'], ssid=ap['ssid']))

            self.request.registry.notify(ContestEventUpdated(self.request, self.context, event))
            self.request.session.flash('Your contest/event has been updated!', queue='event')

            # Depending on what route was matched we do something different.
            if self.request.matched_route.name == "defcne.magic":
                return HTTPSeeOther(location = self.request.resource_url(self.context))
            else:
                return HTTPSeeOther(location = self.request.resource_url(self.context, 'manage'))
        except ValidationFailure, ef:
            return {
                'form': ef.render(),
                'page_title': 'Edit contest/event: {}'.format(event.disp_name),
                'event': e,
                }

        return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'edit')))

    @view_config(context='..acl.Event', name='manage', renderer='event/manage.mako', permission='manage')
    def manage(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['description'] = event.description
        e['logo'] = self.request.registry.settings['defcne.upload_path'] + event.logo if event.logo else ''
        e['website'] = event.website
        e['tables'] = event.tables
        e['chairs'] = event.chairs
        e['owner'] = [x.disp_uname for x in event.owner]
        e['pocs'] = [x.name for x in event.pocs]
        e['requests'] = m.Ticket.count_event_tickets(event.id)
        e['status'] = status_types[event.status]
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'extrainfo'))

        return {
                'page_title': "Manage contest/event: {}".format(event.disp_name),
                'event': e,
                }

    @view_config(context='..acl.Event', name='extrainfo', renderer='event/extrainfo.mako', permission='edit')
    def extrainfo(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['tickets'] = m.Ticket.find_event_tickets(event.id)
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'extrainfo'))

        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        return {
                'page_title': 'Additional info for contest/event: {}'.format(event.disp_name),
                'event': e,
                'form': f.render(),
                }

    @view_config(context='..acl.Event', name='extrainfo', renderer='event/extrainfo.mako', permission='edit', request_method='POST')
    def extrainfo_submit(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['tickets'] = []
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.shortname, 'extrainfo'))

        controls = self.request.POST.items()
        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = f.validate(controls)

            if len(appstruct['ticket']) == 0:
                return HTTPSeeOther(location = self.request.current_route_url())

            ticket = m.Ticket(ticket=appstruct['ticket'], user=self.request.user.user)
            event.tickets.append(ticket)

            self.request.registry.notify(ContestEventTicketUpdated(ticket, self.request, self.context, event))
            self.request.session.flash('Your updated information has been added.', queue='event_info')
            return HTTPSeeOther(location = self.request.current_route_url())

        except ValidationFailure, ef:
            return {
                'page_title': 'Additional info for contest/event: {}'.format(event.disp_name),
                'event': e,
                'form': ef.render(),
                }

