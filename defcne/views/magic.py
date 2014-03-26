# File: magic.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-04-01

import logging
log = logging.getLogger(__name__)

from uuid import uuid4

from pyramid.view import (
        view_config,
        view_defaults,
        )
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import (
        HTTPSeeOther,
        HTTPNotFound,
        )

import transaction

from sqlalchemy.exc import IntegrityError
from deform import (Form, ValidationFailure)

from ..forms import (
        TicketForm,
        MagicUserEdit,
        EventManagement,
        )

from .. import models as m
from ..models.cvebase import (
        status_types,
        badge_types,
        )

@view_defaults(context='..acl.Magic', containment='..acl.Magic', route_name='defcne.magic', permission='magic')
class Magic(object):
    """View for Magic functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(containment=None, renderer='magic/main.mako')
    def main(self):
        return {
                'page_title': 'Magic Portal',
                }

    @view_config(context='..acl.Events')
    def dcyears(self):
        return HTTPSeeOther(location=self.request.route_url('defcne.magic', traverse=('events', '22')))

    @view_config(context='..acl.DefconEvent', renderer='magic/cves.mako')
    def dcevents(self):
        all_events = m.DBSession.query(m.Event).filter(m.Event.dc == self.context.__name__).order_by(m.Event.name.asc())

        if 'filter' in self.request.GET:
            try:
                filterby = int(self.request.GET['filter'])
                all_events = all_events.filter(m.Event.status == filterby)
            except ValueError:
                pass

        all_events = all_events.all()

        events = []
        for event in all_events:
            e = event.to_appstruct()
            e['owner'] = event.owner.disp_uname
            e['status'] = status_types[event.status]
            e['edit_url'] = ('Edit', self.request.resource_url(self.context, event.id, 'edit'))
            e['manage_url'] = ('Manage', self.request.resource_url(self.context, event.id, 'manage'))
            e['magic_url'] = (e['disp_name'], self.request.resource_url(self.context, event.id))
            e['buttons'] = [e['edit_url'], e['manage_url']]
            events.append(e)

        listitems = [
                ('magic_url', 'Event Name', 'url'),
                ('owner', 'Owner', 'text'),
                ('oneliner', 'Summary', 'text'),
                ('status', 'Status', 'text'),
                ('buttons', '', 'buttons'),
                ]

        return {
                'page_title': 'All Events',
                'cves': events,
                'listitems': listitems,
                }

    @view_config(context='..acl.DefconContest', renderer='magic/cves.mako')
    def dccontests(self):
        all_contests = m.DBSession.query(m.Contest).filter(m.Contest.dc == self.context.__name__).order_by(m.Contest.name.asc())

        if 'filter' in self.request.GET:
            try:
                filterby = int(self.request.GET['filter'])
                all_contests = all_contests.filter(m.Contest.status == filterby)
            except ValueError:
                pass

        all_contests = all_contests.all()

        contests = []
        for contest in all_contests:
            e = contest.to_appstruct()
            e['owner'] = contest.owner.disp_uname
            e['status'] = status_types[contest.status]
            e['edit_url'] = ('Edit', self.request.resource_url(self.context, contest.id, 'edit'))
            e['manage_url'] = ('Manage', self.request.resource_url(self.context, contest.id, 'manage'))
            e['magic_url'] = (e['disp_name'], self.request.resource_url(self.context, contest.id))
            e['buttons'] = [e['edit_url'], e['manage_url']]
            contests.append(e)

        listitems = [
                ('magic_url', 'Contest Name', 'url'),
                ('owner', 'Owner', 'text'),
                ('oneliner', 'Summary', 'text'),
                ('status', 'Status', 'text'),
                ('buttons', '', 'buttons'),
                ]

        return {
                'page_title': 'All Contests',
                'cves': contests,
                'listitems': listitems,
                }

    @view_config(context='..acl.DefconVillage', renderer='magic/cves.mako')
    def dcvillages(self):
        all_villages = m.DBSession.query(m.Village).filter(m.Village.dc == self.context.__name__).order_by(m.Village.name.asc())

        if 'filter' in self.request.GET:
            try:
                filterby = int(self.request.GET['filter'])
                all_villages = all_villages.filter(m.Village.status == filterby)
            except ValueError:
                pass

        all_villages = all_villages.all()

        villages = []
        for village in all_villages:
            e = village.to_appstruct()
            e['owner'] = village.owner.disp_uname
            e['status'] = status_types[village.status]
            e['edit_url'] = ('Edit', self.request.resource_url(self.context, village.id, 'edit'))
            e['manage_url'] = ('Manage', self.request.resource_url(self.context, village.id, 'manage'))
            e['magic_url'] = (e['disp_name'], self.request.resource_url(self.context, village.id))
            e['buttons'] = [e['edit_url'], e['manage_url']]
            villages.append(e)

        listitems = [
                ('magic_url', 'Village Name', 'url'),
                ('owner', 'Owner', 'text'),
                ('oneliner', 'Summary', 'text'),
                ('status', 'Status', 'text'),
                ('buttons', '', 'buttons'),
                ]

        return {
                'page_title': 'All Villages',
                'cves': villages,
                'listitems': listitems,
                }

    @view_config(context='..acl.Event', renderer='magic/cve.mako')
    def event(self):
        event = self.context.event

        e = event.to_appstruct()
        e['logo'] = self.request.registry.settings['defcne.upload_path'] + event.logo if event.logo else ''
        e['status'] = status_types[event.status]

        e['owner'] = event.owner.disp_uname
        e['ticket_count'] = len(m.Ticket.find_tickets(event.id))
        e['tickets'] = m.Ticket.find_tickets(event.id)

        e['edit_url'] = ('Edit', self.request.resource_url(self.context, 'edit'))
        e['manage_url'] = ('Manage', self.request.resource_url(self.context, 'manage'))
        e['magic_url'] = (e['disp_name'], self.request.resource_url(self.context))
        e['buttons'] = [e['edit_url'], e['manage_url']]

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
                ('ticket_count', 'Amount of tickets', 'text'),

               ]

        if e['onsite'] and 'space' in e:
            listitems.append(((onsite_listitems, 'space'), 'Onsite Space Requirements', 'sub'))

        listitems.append(('buttons', '', 'buttons'))

        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.resource_url(self.context, 'extrainfo'), buttons=('submit',))

        return {
                'page_title': '{}'.format(event.disp_name),
                'cve': e,
                'listitems': listitems,
                'form': f.render()
                }

    @view_config(context='..acl.Contest', renderer='magic/cve.mako')
    def contest(self):
        contest = self.context.contest

        e = contest.to_appstruct()
        e['logo'] = self.request.registry.settings['defcne.upload_path'] + contest.logo if contest.logo else ''
        e['status'] = status_types[contest.status]

        e['owner'] = contest.owner.disp_uname
        e['ticket_count'] = len(m.Ticket.find_tickets(contest.id))
        e['tickets'] = m.Ticket.find_tickets(contest.id)

        e['edit_url'] = ('Edit', self.request.resource_url(self.context, 'edit'))
        e['manage_url'] = ('Manage', self.request.resource_url(self.context, 'manage'))
        e['magic_url'] = (e['disp_name'], self.request.resource_url(self.context))
        e['buttons'] = [e['edit_url'], e['manage_url']]

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
                ('ticket_count', 'Amount of tickets', 'text'),
                ('buttons', '', 'buttons'),
                ]

        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.resource_url(self.context, 'extrainfo'), buttons=('submit',))

        return {
                'page_title': '{}'.format(contest.disp_name),
                'cve': e,
                'listitems': listitems,
                'form': f.render()
                }

    @view_config(context='..acl.Village', renderer='magic/cve.mako')
    def village(self):
        village = self.context.village

        e = village.to_appstruct()
        e['logo'] = self.request.registry.settings['defcne.upload_path'] + village.logo if village.logo else ''
        e['status'] = status_types[village.status]

        e['owner'] = village.owner.disp_uname
        e['ticket_count'] = len(m.Ticket.find_tickets(village.id))
        e['tickets'] = m.Ticket.find_tickets(village.id)

        e['edit_url'] = ('Edit', self.request.resource_url(self.context, 'edit'))
        e['manage_url'] = ('Manage', self.request.resource_url(self.context, 'manage'))
        e['magic_url'] = (e['disp_name'], self.request.resource_url(self.context))
        e['buttons'] = [e['edit_url'], e['manage_url']]

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
                ('numparticipants', 'Number of participants', 'text'),
                ('years', 'Years Ran', 'text'),
                ('signage', 'Signage', 'text'),
                ((poc_listitems, 'pocs'), 'Points of Contact', 'list'),
                ('quiet_time', 'Quiet Time', 'boolean'),
                ('sharing', 'Sharing', 'boolean'),
                ('buttons', '', 'buttons'),
                ]

        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.resource_url(self.context, 'extrainfo'), buttons=('submit',))

        return {
                'page_title': '{}'.format(village.disp_name),
                'cve': e,
                'listitems': listitems,
                'form': f.render()
                }

    @view_config(context='..acl.Event', name='extrainfo', request_method='POST')
    def event_extrainfo(self):
        event = self.context.event

        controls = self.request.POST.items()
        schema = TicketForm().bind(request=self.request)
        f = Form(schema, action=self.request.resource_url(self.context), buttons=('submit',))

        try:
            appstruct = f.validate(controls)

            if len(appstruct['ticket']) == 0:
                return HTTPSeeOther(location = self.request.resource_url(self.context))

            ticket = m.Ticket(ticket=appstruct['ticket'], user=self.request.user.user)
            event.tickets.append(ticket)

            #self.request.registry.notify(ContestEventTicketUpdated(ticket, self.request, self.context, event))
            self.request.session.flash('The information has been added to the event', queue='event')
            return HTTPSeeOther(location = self.request.resource_url(self.context))

        except ValidationFailure, failed:
            e = event.to_appstruct()
            e['logo'] = self.request.registry.settings['defcne.upload_path'] + event.logo if event.logo else ''
            e['status'] = status_types[event.status]
            e['owner'] = event.owner.disp_uname
            e['ticket_count'] = len(m.Ticket.find_tickets(event.id))
            e['tickets'] = m.Ticket.find_tickets(event.id)

            e['edit_url'] = self.request.resource_url(self.context, event.id, 'edit')
            e['manage_url'] = self.request.resource_url(self.context, event.id, 'manage')
            e['magic_url'] = self.request.resource_url(self.context, event.id)

            return {
                    'page_title': '{}'.format(event.disp_name),
                    'event': e,
                    'form': failed.render()
                    }

    @view_config(context='..acl.Event', name='manage', renderer='magic/edit.mako')
    def event_manage(self):
        event = self.context.event

        astruct = {}
        astruct['status'] = event.status

        # Get badges
        badges = m.DBSession.query(m.Badges).filter(m.Badges.cve_id == event.id).all()

        astruct['badges'] = [{'id': x.id, 'typeof': x.type, 'amount': x.amount, 'why': x.reason} for x in badges]

        schema = EventManagement().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        return {
                'form': f.render(astruct),
                'page_title': 'Manage Event: {}'.format(event.disp_name),
                }


    @view_config(context='..acl.Event', name='manage', renderer='magic/edit.mako', request_method='POST')
    def event_manage_submit(self):
        event = self.context.event

        controls = self.request.POST.items()
        schema = EventManagement().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = f.validate(controls)

            event.status = appstruct['status']

            badges = m.DBSession.query(m.Badges).filter(m.Badges.cve_id == event.id).all()

            new_badge_ids = set([p['id'] for p in appstruct['badges'] if p['id'] != -1])
            cur_badge_ids = set([p.id for p in badges])
            del_badge_ids = cur_badge_ids - new_badge_ids

            if len(del_badge_ids):
                for badge in badges:
                    if badge.id in del_badge_ids:
                        m.DBSession.delete(badge)

            for badge in appstruct['badges']:
                if badge['id'] in cur_badge_ids:
                    cur_badge = [p for p in badges if p.id == badge['id']][0]
                    cur_badge.type = badge['typeof']
                    cur_badge.amount = badge['amount']
                    cur_badge.reason = badge['why']
                else:
                    nbadge = m.Badges(cve_id=event.id, type=badge['typeof'], amount=badge['amount'], reason=badge['why'])
                    m.DBSession.add(nbadge)
                    m.DBSession.flush()

            self.request.session.flash('Event {} has been updated.'.format(event.disp_name), queue='magic')
            return HTTPSeeOther(location = self.request.resource_url(self.context))
        except ValidationFailure, e:
            return {
                    'form': e.render(),
                    'page_title': 'Manage Event: {}'.format(event.disp_name),
                    }


    @view_config(context='..acl.Usernames', renderer='magic/users.mako')
    def users(self):
        all_users = m.DBSession.query(m.User).order_by(m.User.username.asc()).all()

        users = []

        for user in all_users:
            u = {}
            u['username'] = user.disp_uname
            u['email'] = user.email
            u['validated'] = user.validated
            u['groups'] = [x.name for x in user.groups]

            u['view_url'] = self.request.resource_url(self.context, user.username)
            u['edit_url'] = self.request.resource_url(self.context, user.username, 'edit')
            users.append(u)


        return {
                'page_title': 'All Registered Users',
                'users': users,
                }

    @view_config(context='..acl.Username', renderer='magic/user.mako')
    def user(self):
        return {}

    @view_config(context='..acl.Username', name='edit', renderer='magic/edit.mako')
    def user_edit(self):
        user = self.context.user

        schema = MagicUserEdit().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        a = {}
        a['groups'] = [{'group_id': x.id} for x in user.groups]
        a['validated'] = user.validated

        return {
                'page_title': 'Editing user: {}'.format(user.disp_uname),
                'form': f.render(a),
                }


    @view_config(context='..acl.Username', name='edit', renderer='magic/edit.mako', request_method='POST')
    def user_edit_submit(self):
        user = self.context.user

        controls = self.request.POST.items()
        schema = MagicUserEdit().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), button=('submit',))

        try:
            appstruct = f.validate(controls)

            current_groups = set([x.id for x in user.groups])
            selected_groups = set([x['group_id'] for x in appstruct['groups']])
            new_groups = selected_groups - current_groups
            rem_groups = current_groups - selected_groups

            for g in new_groups:
                group = m.Group.find_group_by_id(g)
                user.groups.append(group)

            if len(rem_groups):
                for g in user.groups:
                    if g.id in rem_groups:
                        user.groups.remove(g)

            user.validated = appstruct['validated']

            self.request.session.flash('User {} has been modified.'.format(user.disp_uname), queue='magic')
            return HTTPSeeOther(location = self.request.route_url('defcne.magic', traverse=('u')))
        except ValidationFailure, e:
            return {
                    'form': e.render(),
                    'page_title': 'Editing user: {}'.format(user.disp_uname),
                    }
    @view_config(context='..acl.Badges', renderer='magic/badges.mako')
    def badges(self):
        all_events = m.DBSession.query(m.Event).filter(m.Event.dc == 22).order_by(m.Event.name.asc()).all()

        badgecnt = {}

        for btype in badge_types.keys():
            badgecnt[btype] = 0

        events = []
        for event in all_events:
            if event.status not in [4, 5]:
                continue

            e = {}
            e['name'] = event.disp_name
            e['status'] = status_types[event.status]
            e['blackbadge'] = event.blackbadge
            e['edit_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname, 'edit'))
            e['manage_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname, 'manage'))
            e['magic_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname))

            # Get badges
            badges = m.DBSession.query(m.Badges).filter(m.Badges.cve_id == event.id).all()
            e['badges'] = [{'id': x.id, 'typeof': badge_types[x.type], 'amount': x.amount} for x in badges]

            for badge in badges:
                badgecnt[badge.type] = badgecnt[badge.type] + 1

            events.append(e)

        badgecnts = [{'name': badge_types[key], 'amount': value} for (key, value) in badgecnt.items()]

        return {
                'events': events,
                'count': badgecnts,
                }
