# File: errors.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-05

from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPForbidden

def not_found(request):
    return {}

def forbidden(request):
    # do not allow a user to login if they are already logged in
    if authenticated_userid(request):
        return HTTPForbidden()

    loc = request.route_url('defcne.user.auth', _query=(('next', request.path),))
    return HTTPFound(location=loc)
