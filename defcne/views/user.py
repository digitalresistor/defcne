# File: user.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

from pyramid.httpexceptions import HTTPFound

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
            m.DBSession.flush()
            # Redirect user to waiting on validation
            return HTTPFound(location = self.request.route_url('defcne.user.create.validation'))
        except ValidationFailure, e:
            return {'form': e.render()}
