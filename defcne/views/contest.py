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
        ContestForm,
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

@view_defaults(route_name='defcne.c')
class Contest(object):
    """View for Contest functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(context='..acl.Contests', renderer='event/form.mako', permission='create', name='create', create_allowed=True)
    def create(self):
        (schema, f) = ContestForm.create_form(request=self.request,
            action=self.request.current_route_url(), type='contest')
        return {
                'form': f.render(),
                'page_title': 'Submit Contest Proposal',
                'explanation': None,
                }

    @view_config(context='..acl.Contests', renderer='disabled.mako', permission='create', name='create', create_allowed=False)
    def create_disabled(self):
        self.request.response.status_int = 404
        return {
                'page_title': 'Submit Contest Proposal',
                }

    @view_config(context='..acl.Contests', name='create', renderer='event/form.mako', permission='create', request_method='POST', create_allowed=True)
    def create_submit(self):
        controls = self.request.POST.items()
        (schema, f) = ContestForm.create_form(request=self.request,
                action=self.request.current_route_url(), type='contest')

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

            contest = m.Contest()
            contest.from_appstruct(appstruct)

            contest.owner = self.request.user.user
            contest.dc = 22;

            if appstruct['ticket']:
                ticket = m.Ticket(ticket=appstruct['ticket'], user=self.request.user.user)
                contest.tickets.append(ticket)

            m.DBSession.add(contest)
            m.DBSession.flush()

            self.request.registry.notify(CVECreated(self.request, self.context, contest))
            self.request.session.flash('Your contest has been created. You can make changes at any time. Staff has been notified.', queue='contest')
            return HTTPSeeOther(location = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'manage')))
        except ValidationFailure, e:
            if e.field['csrf_token'].error is not None:
                e.field.error = e.field['csrf_token'].error
                e.field['csrf_token'].cstruct = self.request.session.get_csrf_token()

            return {
                'form': e.render(),
                'page_title': 'Submit Contest Proposal',
                'explanation': None,
                }

    @view_config(context=HTTPForbidden, containment='..acl.Contests', renderer='event/accountneeded.mako')
    def create_not_authed(self):
        return {}

    # If the user attempts to access a page that requires authorization, but
    # they are not logged in, instead of sending them to the login page, we
    # simply send them a not found page. Maybe not as nice for the user if they
    # thought they were logged in, but at least management URL's don't get
    # "advertised" with a "please login =)"
    @view_config(context=HTTPForbidden, containment='..acl.Contest', renderer='not_found.mako')
    def not_authed(self):
        self.request.status_int = 404
        return {}

    @view_config(context='..acl.Contests')
    def main(self):
        return HTTPSeeOther(location = self.request.route_url('defcne.c', traverse='22'))

    @view_config(context='..acl.DefconContest', renderer='cve/all.mako')
    def defcon(self):
        dc = m.Defcon.find_defcon_contests(self.context.__name__)

        if dc is None:
            return {
                    'page_title': 'DEF CON {0}'.format(self.context.__name__),
                    'type': 'contests',
                    'events': []
                    }

        contests = []

        for contest in dc.cve:
            if contest.status != 5:
                continue
            e = contest.to_appstruct()
            e['url'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id))
            contest.append(e)

        return {
                'events': contests,
                'page_title': 'DEF CON {0}'.format(self.context.__name__),
                'type': 'contests',
                }

    @view_config(context='..acl.Contest', renderer='event/one.mako', permission='view')
    def contest(self):
        contest = self.context.contest
        e = contest.to_appstruct()
        e['url'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id))

        return {
                'page_title': '{}'.format(event.disp_name),
                'event': e,
                }

    @view_config(context='..acl.Contest', containment='..acl.Magic', route_name='defcne.magic', name='edit', renderer='magic/edit.mako', permission='magic')
    @view_config(context='..acl.Contest', name='edit', renderer='cve/edit.mako', permission='edit')
    def edit(self):
        contest = self.context.contest

        e = {}
        e['name'] = contest.disp_name
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'extrainfo'))

        astruct = contest.to_appstruct()
        astruct['name'] = astruct['disp_name']

        (schema, f) = ContestForm.create_form(request=self.request,
                action=self.request.current_route_url(), type='contest', origname=contest.name)

        if contest.logo:
            schema['logo'].description = "A logo has already been uploaded. Uploading a new logo will overwrite the previous logo!"
        del astruct['logo']
        del schema['ticket']

        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        return {
                'page_title': 'Edit Contest: {}'.format(contest.disp_name),
                'cve': e,
                'form': f.render(astruct),
                'type': 'contest',
                }

    @view_config(context='..acl.Contest', containment='..acl.Magic', route_name='defcne.magic', name='edit', renderer='magic/edit.mako', request_method='POST', permission='magic')
    @view_config(context='..acl.Contest', name='edit', renderer='cve/edit.mako', permission='edit', request_method='POST')
    def edit_submit(self):
        contest = self.context.contest

        e = {}
        e['name'] = contest.disp_name
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'extrainfo'))

        controls = self.request.POST.items()
        (schema, f) = ContestForm.create_form(request=self.request,
                action=self.request.current_route_url(), type='contest', origname=contest.name)
        del schema['ticket']
        f = Form(schema, action=self.request.current_route_url(), buttons=ContestForm.__buttons__)

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

            self.request.registry.notify(CVEUpdated(self.request, self.context, contest))
            self.request.session.flash('Your contest/contest has been updated!', queue='contest')

            contest.from_appstruct(appstruct)

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
                'page_title': 'Edit Contest: {}'.format(contest.disp_name),
                'cve': e,
                'type': 'contest',
                }

        return HTTPSeeOther(location = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'edit')))

    @view_config(context='..acl.Contest', name='manage', renderer='cve/manage.mako', permission='manage')
    def manage(self):
        contest = self.context.contest

        e = contest.to_appstruct()
        e['logo'] = self.request.registry.settings['defcne.upload_path'] + contest.logo if contest.logo else ''
        e['owner'] = contest.owner.disp_uname
        e['requests'] = m.Ticket.count_tickets(contest.id)
        e['status'] = status_types[contest.status]
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'extrainfo'))

        power_listitems = [
                ('outlets', 'Outlets', 'text'),
                ('justification', 'Justification', 'text'),
                ('threephase', 'Three Phase', 'boolean'),
                ]

        drop_listitems = [
                ('justification', 'Justification', 'text')
                ]

        ap_listitems = [
                ('hwmac', 'HW MAC', 'text'),
                ('apbrand', 'Access Point Brand', 'text'),
                ('ssid', 'SSID', 'text'),
                ]

        poc_listitems = [
                ('name', 'Name', 'text'),
                ('email', 'Email', 'text'),
                ('cellphone', 'Cellphone', 'text'),
                ]

        listitems = [
                ('hrsofoperation', 'Hours of Operation', 'text'),
                ((power_listitems, 'power'), 'Power', 'list'),
                ('spacereq', 'Space Requirements', 'text'),
                ('tables', 'Tables', 'text'),
                ('chairs', 'Chairs', 'text'),
                ('signage', 'Signage', 'text'),
                ('projectors', 'Projectors', 'text'),
                ('screens', 'Screens', 'text'),
                ((drop_listitems, 'drops'), 'Wired Ethernet', 'list'),
                ((ap_listitems, 'aps'), 'Access Points', 'list'),
                ('represent', 'Representation', 'text'),
                ('numparticipants', 'Number of participants', 'text'),
                ('years', 'Years Ran', 'text'),
                ('signage', 'Signage', 'text'),
                ((poc_listitems, 'pocs'), 'Points of Contact', 'list'),
                ('blackbadge_consideration', 'Blackbadge', 'text'),
                ]

        return {
                'page_title': "Manage Contest: {}".format(contest.disp_name),
                'cve': e,
                'listitems': listitems,
                'type': 'Event',
                }

    @view_config(context='..acl.Contest', name='extrainfo', renderer='cve/extrainfo.mako', permission='edit')
    def extrainfo(self):
        contest = self.context.contest

        e = {}
        e['name'] = contest.name
        e['tickets'] = m.Ticket.find_tickets(contest.id)
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'extrainfo'))

        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        return {
                'page_title': 'Additional info for contest: {}'.format(contest.disp_name),
                'cve': e,
                'form': f.render(),
                'type': 'Contest',
                }

    @view_config(context='..acl.Contest', name='extrainfo', renderer='cve/extrainfo.mako', permission='edit', request_method='POST')
    def extrainfo_submit(self):
        contest = self.context.contest

        e = {}
        e['name'] = contest.name
        e['tickets'] = []
        e['url'] = {}
        e['url']['manage'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'manage'))
        e['url']['edit'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'edit'))
        e['url']['extrainfo'] = self.request.route_url('defcne.c', traverse=(contest.dc, contest.id, 'extrainfo'))

        controls = self.request.POST.items()
        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = f.validate(controls)

            if len(appstruct['ticket']) == 0:
                return HTTPSeeOther(location = self.request.current_route_url())

            ticket = m.Ticket(ticket=appstruct['ticket'], user=self.request.user.user)
            contest.tickets.append(ticket)

            self.request.registry.notify(CVETicketUpdated(ticket, self.request, self.context, contest))
            self.request.session.flash('Your updated information has been added.', queue='contest_info')
            return HTTPSeeOther(location = self.request.current_route_url())

        except ValidationFailure, ef:
            if ef.field['csrf_token'].error is not None:
                ef.field.error = ef.field['csrf_token'].error
                ef.field['csrf_token'].cstruct = self.request.session.get_csrf_token()

            return {
                'page_title': 'Additional info for contest/contest: {}'.format(contest.disp_name),
                'cve': e,
                'form': ef.render(),
                'type': 'Contest',
                }


