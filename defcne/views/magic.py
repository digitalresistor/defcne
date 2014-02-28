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

from ..forms import (
        EventManagement,
        TicketForm,
        MagicUserEdit,
        )

from .. import models as m
from ..models.event import (
        status_types,
        badge_types,
        )

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
            e = {}
            e['name'] = event.disp_name
            e['owner'] = [x.disp_uname for x in event.owner]
            e['status'] = status_types[event.status]
            e['blackbadge'] = event.blackbadge
            e['edit_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname, 'edit'))
            e['manage_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname, 'manage'))
            e['magic_url'] = self.request.route_url('defcne.magic', traverse=('e', event.dc, event.shortname))
            events.append(e)

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

        e['pocs'] = [{'name': x.name, 'cellphone': x.cellphone, 'email': x.email} for x in event.pocs]
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

            return {
                    'page_title': '{}'.format(event.disp_name),
                    'event': e,
                    'form': failed.render()
                    }

    def manage(self):
        event = self.context.event

        astruct = {}
        astruct['status'] = event.status
        astruct['blackbadge'] = event.blackbadge

        # Get badges
        badges = m.DBSession.query(m.EventBadges).filter(m.EventBadges.event_id == event.id).all()

        astruct['badges'] = [{'id': x.id, 'typeof': x.type, 'amount': x.amount, 'why': x.reason} for x in badges]

        schema = EventManagement().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        return {
                'form': f.render(astruct),
                'page_title': 'Manage Event: {}'.format(event.disp_name),
                }

    def manage_submit(self):
        event = self.context.event

        controls = self.request.POST.items()
        schema = EventManagement().bind(request=self.request)
        f = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = f.validate(controls)

            event.status = appstruct['status']
            event.blackbadge = appstruct['blackbadge']

            badges = m.DBSession.query(m.EventBadges).filter(m.EventBadges.event_id == event.id).all()

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
                    nbadge = m.EventBadges(event_id=event.id, type=badge['typeof'], amount=badge['amount'], reason=badge['why'])
                    m.DBSession.add(nbadge)
                    m.DBSession.flush()

            self.request.session.flash('Event {} has been updated.'.format(event.disp_name), queue='magic')
            return HTTPSeeOther(location = self.request.route_url('defcne.magic', traverse=('e')))
        except ValidationFailure, e:
            return {
                    'form': e.render(),
                    'page_title': 'Manage Event: {}'.format(event.disp_name),
                    }

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

    def user(self):
        return {}

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
    
    def badges(self):
        all_events = m.DBSession.query(m.Event).filter(m.Event.dc == 21).order_by(m.Event.name.asc()).all()

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
            badges = m.DBSession.query(m.EventBadges).filter(m.EventBadges.event_id == event.id).all()
            e['badges'] = [{'id': x.id, 'typeof': badge_types[x.type], 'amount': x.amount} for x in badges]
            
            for badge in badges:
                badgecnt[badge.type] = badgecnt[badge.type] + 1

            events.append(e)

        badgecnts = [{'name': badge_types[key], 'amount': value} for (key, value) in badgecnt.items()]

        return {
                'events': events,
                'count': badgecnts,
                }
