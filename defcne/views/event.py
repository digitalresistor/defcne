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
        CVECreated,
        CVEUpdated,
        CVEUpdated,
        CVETicketUpdated,
        )

from .. import models as m
from ..models.cvebase import status_types

@view_defaults(route_name='defcne.e')
class Event(object):
    """View for Event functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(context='..acl.Events', renderer='event/form.mako', permission='create', name='create')
    def create(self):
        (schema, f) = EventForm.create_form(request=self.request,
            action=self.request.current_route_url(), type='event')
        return {
                'form': f.render(),
                'page_title': 'Submit Event Proposal',
                'explanation': None,
                }

    @view_config(context='..acl.Events', name='create', renderer='event/form.mako', permission='create', request_method='POST')
    def create_submit(self):
        controls = self.request.POST.items()
        (schema, f) = EventForm.create_form(request=self.request,
                action=self.request.current_route_url(), type='event')

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

            event = m.Event()
            event.from_appstruct(appstruct)

            event.owner = self.request.user.user
            event.dc = 22;

            if appstruct['ticket']:
                ticket = m.Ticket(ticket=appstruct['ticket'], user=self.request.user.user)
                event.tickets.append(ticket)

            m.DBSession.add(event)
            m.DBSession.flush()

            self.request.registry.notify(CVECreated(self.request, self.context, event))
            self.request.session.flash('Your event has been created. You can make changes at any time. Staff has been notified.', queue='event')
            return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'manage')))
        except ValidationFailure, e:
            if e.field['csrf_token'].error is not None:
                e.field.error = e.field['csrf_token'].error
                e.field['csrf_token'].cstruct = self.request.session.get_csrf_token()

            return {
                'form': e.render(),
                'page_title': 'Submit Event Proposal',
                'explanation': None,
                }

    @view_config(context=HTTPForbidden, containment='..acl.Events', renderer='event/accountneeded.mako')
    def create_not_authed(self):
        return {}

    # If the user attempts to access a page that requires authorization, but
    # they are not logged in, instead of sending them to the login page, we
    # simply send them a not found page. Maybe not as nice for the user if they
    # thought they were logged in, but at least management URL's don't get
    # "advertised" with a "please login =)"
    @view_config(context=HTTPForbidden, containment='..acl.Event', renderer='not_found.mako')
    def not_authed(self):
        self.request.status_int = 404
        return {}

    @view_config(context='..acl.Events')
    def main(self):
        return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse='22'))

    @view_config(context='..acl.DefconEvent', renderer='cve/all.mako')
    def defcon(self):
        dc = m.Defcon.find_defcon_events(self.context.__name__)

        if dc is None:
            return {
                    'page_title': 'DEF CON {0}'.format(self.context.__name__),
                    'type': 'events',
                    'events': []
                    }

        events = []

        for event in dc.cve:
            if event.status != 5:
                continue
            e = event.to_appstruct()
            e['url'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id))
            events.append(e)

        return {
                'events': events,
                'page_title': 'DEF CON {0}'.format(self.context.__name__),
                'type': 'events',
                }

    @view_config(context='..acl.Event', renderer='event/one.mako', permission='view')
    def event(self):
        event = self.context.event
        e = event.to_appstruct()
        e['url'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id))

        return {
                'page_title': '{}'.format(event.disp_name),
                'event': e,
                }

    @view_config(context='..acl.Event', containment='..acl.Magic', route_name='defcne.magic', name='edit', renderer='magic/edit.mako', permission='magic')
    @view_config(context='..acl.Event', name='edit', renderer='cve/edit.mako', permission='edit')
    def edit(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'extrainfo'))

        astruct = event.to_appstruct()
        astruct['name'] = astruct['disp_name']

        (schema, f) = EventForm.create_form(request=self.request,
                action=self.request.current_route_url(), type='event')

        if event.logo:
            schema['logo'].description = "A logo has already been uploaded. Uploading a new logo will overwrite the previous logo!"
        del astruct['logo']
        del schema['ticket']

        f = Form(schema, action=self.request.current_route_url(), buttons=EventForm.__buttons__)

        return {
                'page_title': 'Edit contest/event: {}'.format(event.disp_name),
                'cve': e,
                'form': f.render(astruct),
                'type': 'event',
                }

    @view_config(context='..acl.Event', containment='..acl.Magic', route_name='defcne.magic', name='edit', renderer='magic/edit.mako', request_method='POST', permission='magic')
    @view_config(context='..acl.Event', name='edit', renderer='cve/edit.mako', permission='edit', request_method='POST')
    def edit_submit(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'extrainfo'))

        controls = self.request.POST.items()
        (schema, f) = EventForm.create_form(request=self.request,
                action=self.request.current_route_url(), type='event', origname=event.name)
        del schema['ticket']
        f = Form(schema, action=self.request.current_route_url(), buttons=EventForm.__buttons__)

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

            appstruct['logo_path'] = logo_path

            event.from_appstruct(appstruct)

            self.request.registry.notify(CVEUpdated(self.request, self.context, event))
            self.request.session.flash('Your contest/event has been updated!', queue='event')

            # Depending on what route was matched we do something different.
            if self.request.matched_route.name == "defcne.magic":
                return HTTPSeeOther(location = self.request.resource_url(self.context))
            else:
                return HTTPSeeOther(location = self.request.resource_url(self.context, 'manage'))
        except ValidationFailure, ef:
            if ef.field['csrf_token'].error is not None:
                ef.field.error = ef.field['csrf_token'].error
                ef.field['csrf_token'].cstruct = self.request.session.get_csrf_token()

            return {
                'form': ef.render(),
                'page_title': 'Edit contest/event: {}'.format(event.disp_name),
                'cve': e,
                'type': 'event',
                }

        return HTTPSeeOther(location = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'edit')))

    @view_config(context='..acl.Event', name='manage', renderer='cve/manage.mako', permission='manage')
    def manage(self):
        event = self.context.event

        e = event.to_appstruct()
        e['logo'] = self.request.registry.settings['defcne.upload_path'] + event.logo if event.logo else ''
        e['owner'] = event.owner.disp_uname
        e['requests'] = m.Ticket.count_tickets(event.id)
        e['status'] = status_types[event.status]
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'extrainfo'))

        poc_listitems = [
                ('name', 'Name', 'text'),
                ('email', 'Email', 'text'),
                ('cellphone', 'Cellphone', 'text'),
                ]

        onsite_listitems = [
                ('tables', 'Tables', 'text'),
                ('chairs', 'Chairs', 'text'),
                ('stage', 'Stage', 'boolean'),
                ('location', 'Location', 'text'),
                ('mobilebar', 'Mobile Bar', 'text'),
                ]

        listitems = [
                ('onsite', 'Onsite', 'boolean'),
                ('official', 'Official', 'boolean'),
                ('security', 'Security', 'boolean'),
                ('signage', 'Signage', 'text'),
                ((poc_listitems, 'pocs'), 'Points of Contact', 'list'),
                ]

        if e['onsite'] and 'space' in e:
            listitems.append(((onsite_listitems, 'space'), 'Onsite Space Requirements', 'sub'))

        return {
                'page_title': "Manage Event: {}".format(event.disp_name),
                'cve': e,
                'listitems': listitems,
                'type': 'Event',
                }

    @view_config(context='..acl.Event', name='extrainfo', renderer='cve/extrainfo.mako', permission='edit')
    def extrainfo(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['tickets'] = m.Ticket.find_tickets(event.id)
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'extrainfo'))

        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        return {
                'page_title': 'Additional info for event: {}'.format(event.disp_name),
                'cve': e,
                'form': f.render(),
                'type': 'Event',
                }

    @view_config(context='..acl.Event', name='extrainfo', renderer='cve/extrainfo.mako', permission='edit', request_method='POST')
    def extrainfo_submit(self):
        event = self.context.event

        e = {}
        e['name'] = event.name
        e['tickets'] = []
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'extrainfo'))

        controls = self.request.POST.items()
        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = f.validate(controls)

            if len(appstruct['ticket']) == 0:
                return HTTPSeeOther(location = self.request.current_route_url())

            ticket = m.Ticket(ticket=appstruct['ticket'], user=self.request.user.user)
            event.tickets.append(ticket)

            self.request.registry.notify(CVETicketUpdated(ticket, self.request, self.context, event))
            self.request.session.flash('Your updated information has been added.', queue='event_info')
            return HTTPSeeOther(location = self.request.current_route_url())

        except ValidationFailure, ef:
            if ef.field['csrf_token'].error is not None:
                ef.field.error = ef.field['csrf_token'].error
                ef.field['csrf_token'].cstruct = self.request.session.get_csrf_token()

            return {
                'page_title': 'Additional info for event: {}'.format(event.disp_name),
                'cve': e,
                'form': ef.render(),
                'type': 'Event',
                }

