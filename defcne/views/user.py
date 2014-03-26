# File: user.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

import logging
log = logging.getLogger(__name__)

from uuid import uuid4

from pyramid.view import (
        view_config,
        view_defaults,
        )
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPSeeOther, HTTPNotFound

import transaction

from sqlalchemy.exc import IntegrityError
from deform import (Form, ValidationFailure)

from ..forms import (
        UserForm,
        ValidateForm,
        LoginForm,
        LostPassword,
        ResetForm,
        SetPassword,
        )

from ..forms.User import (
        validate_token_matches,
        login_username_password_matches,
        lost_password_username_email_matches,
        reset_token_matches,
        username_password_matches,
        )

from .. import models as m
from ..models.cvebase import status_types as event_status_types

from ..auth import (
        remember,
        forget,
        )

from ..events import (
        UserRegistered,
        UserForgetPassword,
        UserChangedPassword,
        )

_auth_explain = """
<p>If you have a user account you may authenticate to the left, if you do not currently have an account you may <a href="{create_url}">create an account</a>.</p>
<p>If you have forgotten your username and password please visit the <a href="{forgot_url}">forgot my password</a> page.</p>
"""

_create_explain = """
<p>If you already have a user account, you may wish to <a href="{auth_url}">authenticate</a>.</p>
<h3>Why do I need an account?</h3>
<p>You only need to create a user account when you are planning on submitting a contest or event to run at DEF CON. We require an account so that we have a central location to contact event owners/event staff.</p>
<p>It also allows us to track who is in charge of what events so that we don't have any imposters attempting to impersonate you and or your contest.</p>
"""

_validate_explain = """
<p>An email has been sent to the email address you provided us. Please click the contained link or copy and paste the token into the web form.</p>
"""

_forgot_password_explain = """
<p>If you have forgotten your password you may attempt to reset it by providing your username/email address. We will at that point send you a link to be able to reset your password</p>
<p>If you already have an user account, you may wish to <a href="{auth_url}">authenticate</a>.</p>
<p>If you do not yet have a user account you may create <a href="{create_url}">create an account</a>.</p>
"""

_reset_explain = """
<p>An email has been sent to the email address you provided us. Please click the contained link, or copy and paste the token into the web form.</p>
<p>If you remember your password, you may instead wish to <a href="{auth_url}">authenticate</a>. If you don't have an account, you may <a href="{create_url}">create an account</a>.</p>
"""

@view_defaults(route_name='defcne.user')
class User(object):
    """View for User functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name='create', renderer='user/form.mako')
    def create(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        schema = UserForm().bind(request=self.request)
        uf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
        return {
                'form': uf.render(),
                'page_title': 'Create User',
                'explanation': _create_explain.format(auth_url=self.request.route_url('defcne.user', traverse='auth')),
                }

    @view_config(name='create', renderer='user/form.mako', request_method='POST')
    def create_submit(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        controls = self.request.POST.items()
        schema = UserForm().bind(request=self.request)
        uf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = uf.validate(controls)
            # Add the user to the database
            user = m.User(username=appstruct['username'], realname=appstruct['realname'], email=appstruct['email'], credentials=appstruct['password'], cellphone=appstruct['phone'])
            m.DBSession.add(user)
            try:
                m.DBSession.flush()
            except IntegrityError, e:
                return HTTPFound(location = self.request.current_route_url())

            # Create new validation token
            while 1:
                sp = transaction.savepoint()
                try:
                    uservalidation = m.UserValidation(user_id=user.id, token=unicode(uuid4()))
                    m.DBSession.add(uservalidation)
                    m.DBSession.flush()
                    break
                except IntegrityError, e:
                    sp.rollback()
                    continue

            validate_url = self.request.route_url('defcne.user', traverse='validate', _query=(('username', user.username), ('token', uservalidation.token)))

            self.request.registry.notify(UserRegistered(self.request, self.context, user, validate_url=validate_url, token=uservalidation.token))
            log.info("Created a new user \"{user}\" with token \"{token}\". {url}".format(user=user.username, token=uservalidation.token, url=validate_url))

            self.request.session.flash('Your account has been created, an validation email has been sent to your email address.', queue='user')
            return HTTPSeeOther(location = self.request.route_url('defcne.user', traverse='validate'))
        except ValidationFailure, e:
            return {
                    'form': e.render(),
                    'page_title': 'Create User',
                    'explanation': _create_explain.format(auth_url=self.request.route_url('defcne.user', traverse='auth')),
                    }

    def _validate_form(self, controls):
        schema = ValidateForm(validator=validate_token_matches).bind(request=self.request)
        vf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = vf.validate(controls)
            m.DBSession.delete(appstruct['_internal']['validation'])
            user = appstruct['_internal']['user']
            user.validated = True

            headers = remember(self.request, appstruct['username'])
            log.info('User "{user}" has been validated.'.format(user=appstruct['username']))
            self.request.session.flash('Your email has been validated, and your account has been successfully activated.', queue='user')
            return HTTPSeeOther(location = self.request.route_url('defcne.user', traverse=''), headers=headers)

        except ValidationFailure, e:
            return {
                    'form': e.render(),
                    'page_title': 'Validate Email Address',
                    'explanation': _validate_explain,
                    }
    @view_config(name='validate', renderer='user/form.mako')
    def validate(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        if 'username' in self.request.GET and 'token' in self.request.GET:
            self.request.GET['csrf_token'] = self.request.session.get_csrf_token()
            controls = self.request.GET.items()
            return self._validate_form(controls)

        schema = ValidateForm(validator=validate_token_matches).bind(request=self.request)
        vf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
        return {
                'form': vf.render(),
                'page_title': 'Validate Email Address',
                'explanation': _validate_explain,
                }

    @view_config(name='validate', renderer='user/form.mako', request_method='POST')
    def validate_submit(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        controls = self.request.POST.items()
        return self._validate_form(controls)

    @view_config(name='auth', renderer='user/form.mako')
    def auth(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        next_loc = self.request.params.get('next')

        action_loc = self.request.current_route_url() if next_loc is None else self.request.current_route_url(_query=(('next', next_loc),))
        schema = LoginForm(validator=login_username_password_matches).bind(request=self.request)
        af = Form(schema, action=action_loc, buttons=('submit',))
        return {
                'form': af.render(),
                'page_title': 'Authenticate',
                'explanation': _auth_explain.format(create_url=self.request.route_url('defcne.user', traverse='create'), forgot_url=self.request.route_url('defcne.user', traverse='forgot')),
                }

    @view_config(name='auth', renderer='user/form.mako', request_method='POST')
    def auth_submit(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        controls = self.request.POST.items()
        schema = LoginForm(validator=login_username_password_matches).bind(request=self.request)
        af = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = af.validate(controls)
            user = appstruct['_internal']['user']

            if user.validated is False:
                # Create new validation token
                while 1:
                    sp = transaction.savepoint()
                    try:
                        uservalidation = m.UserValidation(user_id=user.id, token=unicode(uuid4()))
                        m.DBSession.add(uservalidation)
                        m.DBSession.flush()
                        break
                    except IntegrityError, e:
                        sp.rollback()
                        continue

                validate_url = self.request.route_url('defcne.user', traverse='validate', _query=(('username', user.username), ('token', uservalidation.token)))

                self.request.registry.notify(UserRegistered(self.request, self.context, user, validate_url=validate_url, token=uservalidation.token))
                log.info("Resent validation email for \"{user}\" with token \"{token}\". {url}".format(user=user.username, token=uservalidation.token, url=validate_url))
                self.request.session.flash('Your account still needs to be validated, please check your email account. The email has been resent to {email}'.format(email=user.email), queue='user')
                return HTTPSeeOther(location = self.request.route_url('defcne.user', traverse='validate'))

            headers = remember(self.request, user.username)
            log.info('Logging in "{user}"'.format(user=user.username))

            # Invalidate any outstanding reset tokens
            if user.credreset:
                user.credreset = False

            next_loc = self.request.params.get('next') or ''
            next_loc = [loc for loc in next_loc.split('/') if loc != '']
            location = self.request.route_url('defcne') if next_loc is None else self.request.route_url('defcne', *next_loc)
            return HTTPSeeOther(location = location, headers=headers)
        except ValidationFailure, e:
            return {
                    'form': e.render(),
                    'page_title': 'Authenticate',
                    'explanation': _auth_explain.format(create_url=self.request.route_url('defcne.user', traverse='create'), forgot_url=self.request.route_url('defcne.user', traverse='forgot')),
                    }

    @view_config(name='deauth')
    def deauth(self):
        headers = forget(self.request)
        return HTTPSeeOther(location = self.request.route_url('defcne'), headers=headers)

    @view_config(renderer='user/user.mako', permission='view')
    def user(self):
        events = m.DBSession.query(m.CVEBase).filter(m.CVEBase.owner == self.request.user.user).order_by(m.CVEBase.disp_name).all()

        eventlist = []
        for event in events:
            event_info = event.to_appstruct()
            event_info['status'] = event_status_types[event.status]

            if event.type == 'contest':
                event_info['url'] = self.request.route_url('defcne.c', traverse=(event.dc, event.id, 'manage'))
            if event.type == 'event':
                event_info['url'] = self.request.route_url('defcne.e', traverse=(event.dc, event.id, 'manage'))
            if event.type == 'village':
                event_info['url'] = self.request.route_url('defcne.v', traverse=(event.dc, event.id, 'manage'))

            eventlist.append(event_info)

        return {
                'page_title': 'User',
                'events': eventlist,
                }

    @view_config(name='edit', renderer='user/form_menu.mako', permission='edit')
    def edit(self):
        # Redirect to the right location if the user just went to /user/edit/
        if len(self.request.subpath) == 0:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=('edit', 'profile')))

        if 'password' == self.request.subpath[0]:
            return self.edit_password()

        if 'profile' == self.request.subpath[0]:
            return self.edit_profile()

        raise HTTPNotFound()

    @view_config(name='edit', renderer='user/form_menu.mako', permission='edit', request_method='POST')
    def edit_submit(self):
        if 'password' == self.request.subpath[0]:
            return self.edit_password_submit()
        if 'profile' == self.request.subpath[0]:
            return self.edit_profile_submit()

        raise HTTPNotFound()

    def edit_password(self):
        if self.request.user.user.credreset:
            schema = SetPassword().clone()
            del schema['password']
            schema.bind(request=self.request)
        else:
            schema = SetPassword(validator=username_password_matches)

        schema = schema.bind(request=self.request)

        epf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        return {
                'page_title': "Change password",
                'form': epf.render(),
                }

    def edit_password_submit(self):
        if self.request.user.user.credreset:
            schema = SetPassword().clone()
            del schema['password']
        else:
            schema = SetPassword(validator=username_password_matches)

        controls = self.request.POST.items()
        schema = schema.bind(request=self.request)
        epf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = epf.validate(controls)
            user = self.request.user.user
            user.credreset = False
            user.credentials = appstruct['new_password']

            m.DBSession.query(m.UserForgot).filter(m.UserForgot.user_id == user.id).delete()
            m.DBSession.query(m.UserTickets).filter(m.UserTickets.user_id == user.id).delete()

            self.request.session.flash('Password has been updated!', queue='user')
            self.request.registry.notify(UserChangedPassword(self.request, self.context, user))
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))
        except ValidationFailure, e:
            return {
                    'page_title': "Change password",
                    'form': e.render(),
                    }

    def edit_profile(self):
        return {
                'page_title': "Edit user profile",
                }

    def edit_profile_submit(self):
        return {}

    @view_config(name='forgot', renderer='user/form.mako')
    def forgot(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        schema = LostPassword(validator=lost_password_username_email_matches).bind(request=self.request)
        lpf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
        return {
                'form': lpf.render(),
                'page_title': 'Forgot Password',
                'explanation': _forgot_password_explain.format(create_url=self.request.route_url('defcne.user', traverse='create'), auth_url=self.request.route_url('defcne.user', traverse='auth')),
                }

    @view_config(name='forgot', renderer='user/form.mako', request_method='POST')
    def forgot_submit(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        controls = self.request.POST.items()
        schema = LostPassword(validator=lost_password_username_email_matches).bind(request=self.request)
        lpf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = lpf.validate(controls)
            user = appstruct['_internal']['user']
            user.credreset = True

            # Remove all previously generated tokens if they still exist ... basically we want to make sure we invalidate all previous attempts
            m.DBSession.query(m.UserForgot).filter(m.UserForgot.user_id == user.id).delete()

            # Create new token
            userforgot = m.UserForgot(user_id=user.id, token=unicode(uuid4()))
            m.DBSession.add(userforgot)

            reset_url = self.request.route_url('defcne.user', traverse='reset', _query=(('username', user.username), ('token', userforgot.token)))

            self.request.registry.notify(UserForgetPassword(self.request, self.context, user, reset_url=reset_url, token=userforgot.token))
            log.info("User \"{user}\" forgot password, generated token \"{token}\". {url}".format(user=user.username, token=userforgot.token, url=reset_url))

            location = self.request.route_url('defcne.user', traverse='reset')
            return HTTPSeeOther(location = location)
        except ValidationFailure, e:
            return {
                    'form': e.render(),
                    'page_title': 'Forgot Password',
                    'explanation': _forgot_password_explain.format(create_url=self.request.route_url('defcne.user', traverse='create'), auth_url=self.request.route_url('defcne.user', traverse='auth')),
                    }

    def _reset_form(self, controls):
        schema = ResetForm(validator=reset_token_matches).bind(request=self.request)
        rf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = rf.validate(controls)
            user = appstruct['_internal']['user']
            m.DBSession.query(m.UserForgot).filter(m.UserForgot.user_id == user.id).delete()
            m.DBSession.query(m.UserTickets).filter(m.UserTickets.user_id == user.id).delete()

            user.credreset = True

            headers = remember(self.request, user.username)
            log.info('User "{user}" has requested to reset password. They are now logged in, sending to main page.'.format(user=appstruct['username']))
            return HTTPSeeOther(location = self.request.route_url('defcne.user', traverse='edit/password'), headers=headers)
        except ValidationFailure, e:
            return {
                    'form': e.render(),
                    'page_title': 'Reset Password',
                    'explanation': _reset_explain.format(auth_url=self.request.route_url('defcne.user', traverse='auth'), create_url=self.request.route_url('defcne.user', traverse='create')),
                    }
    @view_config(name='reset', renderer='user/form.mako')
    def reset(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        if 'username' in self.request.GET and 'token' in self.request.GET:
            self.request.GET['csrf_token'] = self.request.session.get_csrf_token()
            controls = self.request.GET.items()
            return self._reset_form(controls)

        schema = ResetForm(validator=reset_token_matches).bind(request=self.request)
        rf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
        return {
                'form': rf.render(),
                'page_title': 'Reset Password',
                'explanation': _reset_explain.format(auth_url=self.request.route_url('defcne.user', traverse='auth'), create_url=self.request.route_url('defcne.user', traverse='create')),
                }
    @view_config(name='reset', renderer='user/form.mako', request_method='POST')
    def reset_submit(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        controls = self.request.POST.items()
        return self._validate_form(controls)

    @view_config(name='profile', renderer='user/profile.mako', request_method='GET', permission='view')
    def profile(self):
        pfields = []

        pfields.append(('Real Name', self.request.user.user.realname))
        pfields.append(('Email', self.request.user.user.email))
        pfields.append(('Phone', self.request.user.user.cellphone))
        return {
                'page_title': 'User Profile',
                'profile_fields': pfields,
                }
