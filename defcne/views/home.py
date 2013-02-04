# File: home.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-05

from pyramid.security import authenticated_userid

def home(request):
    return {'user': authenticated_userid(request)}
