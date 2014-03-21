# File: __init__.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-05

import logging
log = logging.getLogger(__name__)

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
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

    _session_factory = SignedCookieSessionFactory(
            settings['pyramid.secretcookie'],
            httponly=True,
            max_age=864000
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
    #config.add_route('defcne.u', '/u/*traverse', factory=acl.Usernames)

    # /user/*traverse
    config.add_route('defcne.user', '/user/*traverse', factory=acl.User)

    # /e/*traverse
    config.add_route('defcne.e', '/events/*traverse', factory=acl.Events)

    # /c/*traverse
    config.add_route('defcne.c', '/contests/*traverse', factory=acl.Contests)

    # /magic/*traverse
    config.add_route('defcne.magic', '/magic/*traverse', factory=acl.Magic)

def add_views(config):
    config.scan('.views')

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
            'defcne.events.CVECreated')
    config.add_subscriber('defcne.subscribers.cne_updated',
            'defcne.events.CVEUpdated')
