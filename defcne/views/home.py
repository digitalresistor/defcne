# File: home.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-05

from pyramid.view import view_config

@view_config(route_name='defcne', renderer='home.mako')
def home(request):
    return {'create_enable': request.registry.settings['defcne.registration_open']}

@view_config(context='pyramid.traversal.DefaultRootFactory', name='guidelines', renderer='guidelines.mako')
def guidelines(self):
    return {}
