# File: user.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

import logging
log = logging.getLogger(__name__)

from uuid import uuid4

from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPSeeOther

import transaction

from sqlalchemy.exc import IntegrityError
from deform import (Form, ValidationFailure)

from ..forms import (
        UserForm,
        ValidateForm,
        LoginForm,
        )

from ..forms.User import (
        validate_token_matches,
        login_username_password_matches
        )

from .. import models as m

from ..auth import (
        remember,
        forget,
        )

_auth_explain = """
<p>If you have a user account you may authenticate to the left, if you do not currently have an account you may <a href="{create_url}">create an account</a>.</p>
<p>If you have forgotten your username and password please visit the <a href="{forgot_url}">forgot my password</a> page.</p>
"""

_create_explain = """
<p>If you already have a user account, you may wish to <a href="{auth_url}">authenticate</a>.</p>
<h3>Why do I need an account?</h3>
<p>You only need to create a user account when you are planning on submitting a contest or event to run at DEFCON. We require an account so that we have a central location to contact event owners/event staff.</p>
<p>It also allows us to track who is in charge of what events so that we don't have any imposters attempting to impersonate you and or your contest.</p>
"""

_validate_explain = """
<p>An email has been sent to the email address you provided us. Please click the contained link or copy and paste the token into the web form.</p>
"""

class User(object):
    """View for User functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

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

    def create_submit(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        controls = self.request.POST.items()
        schema = UserForm().bind(request=self.request)
        uf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = uf.validate(controls)
            # Add the user to the database
            user = m.User(username=appstruct['username'], realname=appstruct['realname'], email=appstruct['email'], credentials=appstruct['password'])
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

            print ("Created a new user \"{user}\" with token \"{token}\"".format(user=user.username, token=uservalidation.token))
            # Send out validation email to email address on for user

            # Redirect user to waiting on validation
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
            m.DBSession.delete(m.UserValidation.find_token(appstruct['token']))
            user = m.User.find_user(appstruct['username'])
            user.validated = True

            headers = remember(self.request, appstruct['username'])
            log.info('User "{user}" has been validated.'.format(user=appstruct['username']))
            return HTTPSeeOther(location = self.request.route_url('defcne.user', traverse='complete'), headers=headers)

        except ValidationFailure, e:
            return {
                    'form': e.render(),
                    'page_title': 'Validate Email Address',
                    'explanation': _validate_explain,
                    }

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

    def validate_submit(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        controls = self.request.POST.items()
        return self._validate_form(controls)

    def complete(self):
        return {}

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

    def auth_submit(self):
        if authenticated_userid(self.request) is not None:
            return HTTPSeeOther(self.request.route_url('defcne.user', traverse=''))

        controls = self.request.POST.items()
        schema = LoginForm(validator=login_username_password_matches).bind(request=self.request)
        af = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = af.validate(controls)
            headers = remember(self.request, appstruct['username'])
            log.info('Logging in "{user}"'.format(user=appstruct['username']))

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

    def deauth(self):
        headers = forget(self.request)
        return HTTPSeeOther(location = self.request.route_url('defcne'), headers=headers)

    def user(self):
        return {}

    def edit(self):
        return {}

    def edit_submit(self):
        return {}

