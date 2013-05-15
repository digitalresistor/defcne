# File: __init__.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-05

import logging
log = logging.getLogger(__name__)

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from pyramid.httpexceptions import HTTPForbidden

import deform_bootstrap

from sqlalchemy import engine_from_config
from sqlalchemy.exc import DBAPIError

from models import DBSession
import auth
import acl

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)

    if not 'pyramid.secretcookie' in settings:
        log.error('pyramid.secretcookie is not set. Refusing to start.')
        quit(-1)

    if not 'pyramid.auth.secret' in settings:
        log.error('pyramid.auth.secret is not set. Refusing to start.')
        quit(-1)

    if not 'defcne.upload_path' in settings:
        log.error('defcne.upload_path is not set. Refusing to start.')
        quit(-1)

    _session_factory = UnencryptedCookieSessionFactoryConfig(
            settings['pyramid.secretcookie'],
            cookie_httponly=True,
            cookie_max_age=864000
            )

    _authn_policy = AuthTktAuthenticationPolicy(
            settings['pyramid.auth.secret'],
            max_age=864000,
            http_only=True,
            debug=True,
            hashalg='sha512',
            callback=auth.user_groups,
            )

    _authz_policy = ACLAuthorizationPolicy()

    config.set_session_factory(_session_factory)
    config.set_authentication_policy(_authn_policy)
    config.set_authorization_policy(_authz_policy)
    config.include(add_routes)
    config.include(add_views)
    config.include(add_events)

    deform_bootstrap.includeme(config)

    config.set_request_property(auth.current_user, 'user', reify=True)
    config.include('pyramid_mailer')
    return config.make_wsgi_app()

def add_routes(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static', cache_max_age=3600)
    config.add_static_view('files', config.registry.settings['defcne.upload_path'], cache_max_age=3600)

    # Routes:
    # /
    config.add_route('defcne', '/')

    # /u/*traverse
    config.add_route('defcne.u', '/u/*traverse', factory=acl.Username)

    # /user/*traverse
    config.add_route('defcne.user', '/user/*traverse', factory=acl.User)

    # /g/*traverse
    config.add_route('defcne.g', '/g/*traverse', factory=acl.Goons)

    # /e/*traverse
    config.add_route('defcne.e', '/e/*traverse', factory=acl.Events)

    # /magic/*traverse
    config.add_route('defcne.magic', '/magic/*traverse', factory=acl.Magic)

def add_views(config):
    config.add_view('defcne.views.home.home',
            route_name='defcne',
            renderer='home.mako')

    # /user/
    config.add_view('defcne.views.User',
            attr='user',
            route_name='defcne.user',
            name='',
            renderer='user/user.mako',
            request_method='GET',
            permission='view')

    # /user/profile
    config.add_view('defcne.views.User',
            attr='profile',
            route_name='defcne.user',
            name='profile',
            renderer='user/profile.mako',
            request_method='GET',
            permission='view')

    # /user/create (GET/POST)
    config.add_view('defcne.views.User',
            attr='create',
            route_name='defcne.user',
            name='create',
            renderer='user/form.mako',
            request_method='GET')

    config.add_view('defcne.views.User',
            attr='create_submit',
            route_name='defcne.user',
            name='create',
            renderer='user/form.mako',
            request_method='POST',
            check_csrf=True)

    # /user/auth (GET/POST)
    config.add_view('defcne.views.User',
            attr='auth',
            route_name='defcne.user',
            name='auth',
            renderer='user/form.mako',
            request_method='GET')

    config.add_view('defcne.views.User',
            attr='auth_submit',
            route_name='defcne.user',
            name='auth',
            renderer='user/form.mako',
            request_method='POST',
            check_csrf=True)

    # /user/deauth
    config.add_view('defcne.views.User',
            attr='deauth',
            route_name='defcne.user',
            name='deauth',
            request_method='GET')

    # /user/validate (GET/POST)
    config.add_view('defcne.views.User',
            attr='validate',
            route_name='defcne.user',
            name='validate',
            renderer='user/form.mako',
            request_method='GET')

    config.add_view('defcne.views.User',
            attr='validate_submit',
            route_name='defcne.user',
            name='validate',
            renderer='user/form.mako',
            request_method='POST',
            check_csrf=True)

    # /user/edit/ (GET/POST)
    config.add_view('defcne.views.User',
            attr='edit',
            route_name='defcne.user',
            name='edit',
            renderer='user/form_menu.mako',
            request_method='GET',
            permission='edit')

    config.add_view('defcne.views.User',
            attr='edit_submit',
            route_name='defcne.user',
            name='edit',
            renderer='user/form_menu.mako',
            request_method='POST',
            permission='edit',
            check_csrf=True)

    # /user/forgot (GET/POST)
    config.add_view('defcne.views.User',
            attr='forgot',
            route_name='defcne.user',
            name='forgot',
            renderer='user/form.mako',
            request_method='GET')

    config.add_view('defcne.views.User',
            attr='forgot_submit',
            route_name='defcne.user',
            name='forgot',
            renderer='user/form.mako',
            request_method='POST',
            check_csrf=True)

    # /user/reset (GET/POST)
    config.add_view('defcne.views.User',
            attr='reset',
            route_name='defcne.user',
            name='reset',
            renderer='user/form.mako',
            request_method='GET')

    config.add_view('defcne.views.User',
            attr='reset_submit',
            route_name='defcne.user',
            name='reset_password',
            renderer='user/form.mako',
            request_method='POST',
            check_csrf=True)

    # /e/guidelines (GET)
    config.add_view('defcne.views.Event',
            attr='guidelines',
            route_name='defcne.e',
            name='guidelines',
            renderer='event/rules.mako',
            request_method='GET')

    # /e/create (GET/POST)
    config.add_view('defcne.views.Event',
            attr='create',
            route_name='defcne.e',
            context=acl.EventCreate,
            renderer='event/form.mako',
            request_method='GET',
            permission='create')

    config.add_view('defcne.views.Event',
            attr='create',
            route_name='defcne.e',
            context=acl.EventCreate,
            name='letsgo',
            renderer='event/form.mako',
            request_method='GET',
            permission='create')

    config.add_view('defcne.views.Event',
            attr='create_submit',
            route_name='defcne.e',
            context=acl.EventCreate,
            name='letsgo',
            renderer='event/form.mako',
            request_method='POST',
            permission='create',
            check_csrf=True)

    config.add_view('defcne.views.Event',
            attr='create_not_authed',
            context=HTTPForbidden,
            containment=acl.EventCreate,
            renderer='event/accountneeded.mako',
            request_method='GET')

    # /e/
    config.add_view('defcne.views.Event',
            attr='main',
            route_name='defcne.e',
            context=acl.Events,
            request_method='GET')

    config.add_view('defcne.views.Event',
            attr='defcon',
            route_name='defcne.e',
            context=acl.DefconEvent,
            renderer='event/all.mako',
            request_method='GET')

    config.add_view('defcne.views.Event',
            attr='event',
            route_name='defcne.e',
            context=acl.Event,
            renderer='event/one.mako',
            request_method='GET',
            permission='view')

    config.add_view('defcne.views.Event',
            attr='manage',
            route_name='defcne.e',
            name='manage',
            context=acl.Event,
            renderer='event/manage.mako',
            request_method='GET',
            permission='manage')

    config.add_view('defcne.views.Event',
            attr='edit',
            route_name='defcne.e',
            name='edit',
            context=acl.Event,
            renderer='event/edit.mako',
            request_method='GET',
            permission='edit')

    config.add_view('defcne.views.Event',
            attr='edit_submit',
            route_name='defcne.e',
            name='edit',
            context=acl.Event,
            renderer='event/edit.mako',
            request_method='POST',
            permission='edit',
            check_csrf=True)

    config.add_view('defcne.views.Event',
            attr='extrainfo',
            route_name='defcne.e',
            name='extrainfo',
            context=acl.Event,
            renderer='event/extrainfo.mako',
            request_method='GET',
            permission='edit')

    config.add_view('defcne.views.Event',
            attr='extrainfo_submit',
            route_name='defcne.e',
            name='extrainfo',
            context=acl.Event,
            renderer='event/extrainfo.mako',
            request_method='POST',
            permission='edit',
            check_csrf=True)

    # If the user attempts to access a page that requires authorization, but
    # they are not logged in, instead of sending them to the login page, we
    # simply send them a not found page. Maybe not as nice for the user if they
    # thought they were logged in, but at least management URL's don't get
    # "advertised" with a "please login =)"
    config.add_view('defcne.views.Event',
            attr='not_authed',
            context=HTTPForbidden,
            containment=acl.Event,
            renderer='not_found.mako',
            request_method='GET')

    # /magic/
    config.add_view('defcne.views.Magic',
            attr='main',
            route_name='defcne.magic',
            name='',
            context=acl.Magic,
            renderer='magic/main.mako',
            request_method='GET',
            permission='magic')

    config.add_view('defcne.views.Magic',
            attr='dcyears',
            route_name='defcne.magic',
            name='',
            context=acl.Events,
            containment=acl.Magic,
            request_method='GET',
            permission='magic')

    config.add_view('defcne.views.Magic',
            attr='dcevents',
            route_name='defcne.magic',
            name='',
            context=acl.DefconEvent,
            containment=acl.Magic,
            renderer='magic/events.mako',
            request_method='GET',
            permission='magic')

    config.add_view('defcne.views.Magic',
            attr='event',
            route_name='defcne.magic',
            name='',
            context=acl.Event,
            containment=acl.Magic,
            renderer='magic/event.mako',
            request_method='GET',
            permission='magic')

    config.add_view('defcne.views.Magic',
            attr='event_extrainfo',
            route_name='defcne.magic',
            name='extrainfo',
            context=acl.Event,
            containment=acl.Magic,
            renderer='magic/event.mako',
            request_method='POST',
            permission='magic',
            check_csrf=True)

    config.add_view('defcne.views.Magic',
            attr='manage',
            route_name='defcne.magic',
            name='manage',
            context=acl.Event,
            containment=acl.Magic,
            renderer='magic/edit.mako',
            request_method='GET',
            permission='magic')

    config.add_view('defcne.views.Magic',
            attr='manage_submit',
            route_name='defcne.magic',
            name='manage',
            context=acl.Event,
            containment=acl.Magic,
            renderer='magic/edit.mako',
            request_method='POST',
            permission='magic',
            check_csrf=True)

    config.add_view('defcne.views.Event',
            attr='edit',
            route_name='defcne.magic',
            name='edit',
            context=acl.Event,
            containment=acl.Magic,
            renderer='magic/edit.mako',
            request_method='GET',
            permission='magic')

    config.add_view('defcne.views.Event',
            attr='edit_submit',
            route_name='defcne.magic',
            name='edit',
            context=acl.Event,
            containment=acl.Magic,
            renderer='magic/edit.mako',
            request_method='POST',
            permission='magic',
            check_csrf=True)

    config.add_view('defcne.views.Magic',
            attr='user',
            route_name='defcne.magic',
            name='',
            context=acl.Username,
            containment=acl.Magic,
            renderer='magic/user.mako',
            request_method='GET',
            permission='magic')

    config.add_view('defcne.views.Magic',
            attr='user_edit',
            route_name='defcne.magic',
            name='edit',
            context=acl.Username,
            containment=acl.Magic,
            renderer='magic/edit.mako',
            request_method='GET',
            permission='magic')

    config.add_view('defcne.views.Magic',
            attr='user_edit_submit',
            route_name='defcne.magic',
            name='edit',
            context=acl.Username,
            containment=acl.Magic,
            renderer='magic/edit.mako',
            request_method='POST',
            permission='magic',
            check_csrf=True)

    config.add_view('defcne.views.Magic',
            attr='users',
            route_name='defcne.magic',
            name='',
            context=acl.Usernames,
            containment=acl.Magic,
            renderer='magic/users.mako',
            request_method='GET',
            permission='magic')

    # Error pages
    #config.add_view('usingnamespace.views.errors.db_failed', context=DBAPIError, renderer='db_failed.mako')

    # Add a slash if the view has not been found.
    config.add_notfound_view('defcne.views.errors.bad_request', renderer='bad_request.mako', request_method='POST')
    config.add_notfound_view('defcne.views.errors.not_found', renderer='not_found.mako', append_slash=True)
    config.add_forbidden_view('defcne.views.errors.forbidden', renderer='forbidden.mako')

def add_events(config):
    config.add_subscriber('defcne.subscribers.user_created',
            'defcne.events.UserRegistered')
    config.add_subscriber('defcne.subscribers.user_forgotpassword',
            'defcne.events.UserForgetPassword')
    config.add_subscriber('defcne.subscribers.user_passwordupdated',
            'defcne.events.UserChangedPassword')
    config.add_subscriber('defcne.subscribers.cne_created',
            'defcne.events.ContestEventCreated')
    config.add_subscriber('defcne.subscribers.cne_updated',
            'defcne.events.ContestEventUpdated')
