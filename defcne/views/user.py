# File: user.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

from uuid import uuid4

from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import remember
from pyramid.httpexceptions import HTTPFound

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

class User(object):
    """View for User functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create(self):
        schema = UserForm().bind(request=self.request)
        uf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
        return {'form': uf.render()}

    def create_submit(self):
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
            return HTTPFound(location = self.request.route_url('defcne.user.create.validate'))
        except ValidationFailure, e:
            return {'form': e.render()}

    def _validate_form(self, controls):
        schema = ValidateForm(validator=validate_token_matches).bind(request=self.request)
        vf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = vf.validate(controls)
            print "Found the token, and the username matches."

            m.DBSession.delete(m.UserValidation.find_token(appstruct['token']))
            # Log the user in if they are here, for one they have access to the email account where reset passwords are sent, so it is not a security issue

            return HTTPFound(location = self.request.route_url('defcne.user.complete'))

        except ValidationFailure, e:
            return {'form': e.render()}

    def validate(self):
        if 'username' in self.request.GET and 'token' in self.request.GET:
            self.request.GET['csrf_token'] = self.request.session.get_csrf_token()
            controls = self.request.GET.items()
            return self._validate_form(controls)

        schema = ValidateForm(validator=validate_token_matches).bind(request=self.request)
        vf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
        return {'form': vf.render()}

    def validate_submit(self):
        controls = self.request.POST.items()
        return self._validate_form(controls)

    def complete(self):
        return {}

    def auth(self):
        schema = LoginForm(validator=login_username_password_matches).bind(request=self.request)
        af = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
        return {'form': af.render()}

    def auth_submit(self):
        controls = self.request.POST.items()
        schema = LoginForm(validator=login_username_password_matches).bind(request=self.request)
        af = Form(schema, action=self.request.current_route_url(), buttons=('submit',))

        try:
            appstruct = af.validate(controls)
            headers = remember(self.request, appstruct['username'])
            return HTTPFound(location = self.request.route_url('defcne.user'), headers=headers)
        except ValidationFailure, e:
            return {'form': e.render()}

    def deauth(self):
        headers = forget(self.request)
        return HTTPFound(location = self.request.route_url('defcne'), headers=headers)

