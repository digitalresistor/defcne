# File: __init__.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-05

import logging
log = logging.getLogger(__name__)

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

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
#    config.include(add_events)

    deform_bootstrap.includeme(config)

    config.set_request_property(auth.current_user, 'user', reify=True)
    return config.make_wsgi_app()

def add_routes(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static', cache_max_age=3600)
    config.add_static_view('files', config.registry.settings['defcne.upload_path'], cache_max_age=3600)

    # Routes:
    # /
    config.add_route('defcne', '/')

    # /u/
    config.add_route('defcne.u', '/u/')

    # /u/<username>/
    config.add_route('defcne.u.username', '/u/{username}/')

    # /u/<username>/contact
    config.add_route('defcne.u.username.contact', '/u/{username}/contact/')

    # /user/*traverse
    config.add_route('defcne.user', '/user/*traverse', factory=acl.User)

    # /g/
    config.add_route('defcne.g', '/g/')

    # /g/<dc>/
    config.add_route('defcne.g.dc', '/g/{defcon:\d{2}/')

    # /g/<dc>/<username>/
    config.add_route('defcne.g.username', '/g/{defcon:\d{2}}/{username}/')

    # /e/
    config.add_route('defcne.events', '/e/')

    # /e/<dc>/
    config.add_route('defcne.events.defcon', '/e/{defcon:\d{2}}/')

    # /e/create/
    config.add_route('defcne.event.create', '/e/create/')

    # /e/<dc>/<eventshort>/
    config.add_route('defcne.event.name', '/e/{defcon:\d{2}}/{eventname}/')

    # /e/<dc>/<eventshort>/edit
    config.add_route('defcne.event.name.edit', '/e/{defcon:\d{2}}/{eventname}/edit/')

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

    # /user/complete
    config.add_view('defcne.views.User',
            attr='complete',
            route_name='defcne.user',
            name='complete',
            renderer='user/complete.mako',
            request_method='GET',
            permission='view')

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

    # Error pages
    #config.add_view('usingnamespace.views.errors.db_failed', context=DBAPIError, renderer='db_failed.mako')

    # Add a slash if the view has not been found.
    config.add_notfound_view('defcne.views.errors.bad_request', renderer='bad_request.mako', request_method='POST')
    config.add_notfound_view('defcne.views.errors.not_found', renderer='not_found.mako', append_slash=True)
    config.add_forbidden_view('defcne.views.errors.forbidden', renderer='not_found.mako')

def add_events(config):
    pass
#    config.add_subscriber('usingnamespace.events.view_helpers.view_helpers',
#            'pyramid.events.BeforeRender')
