# File: user.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

from uuid import uuid4

import transaction
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import IntegrityError
from deform import (Form, ValidationFailure)

from ..forms import UserForm
from .. import models as m

class User(object):
    """View for User functionality"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create(self):
        print "Running create function ..."
        schema = UserForm().bind(request=self.request)
        uf = Form(schema, action=self.request.current_route_url(), buttons=('submit',))
        return {'form': uf.render()}

    def create_submit(self):
        print "Running create_submit"

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

            sp = transaction.savepoint()
            while 1:
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
            return HTTPFound(location = self.request.route_url('defcne.user.create.validation'))
        except ValidationFailure, e:
            return {'form': e.render()}
