# File: acl.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-02-08

from pyramid.security import (
        ALL_PERMISSIONS,
        Allow,
        Authenticated,
        Deny,
        Everyone,
        )

class User(object):
    permissions = {
            'edit': [
                (Allow, Authenticated, 'edit'),
                ],
            'complete': [
                (Allow, Authenticated, 'view'),
                ],
            }

    @property
    def __acl__(self):
        if self.key is not None:
            return self.permissions[self.key]
        return [
                (Allow, Authenticated, 'view'),
                ]

    def __init__(self, request):
        self.key = None

    def __getitem__(self, key):
        # We use the key if available to set the permissions for the context,
        # but besides that we don't use it!
        if key in self.permissions:
            self.key = key
        
        raise KeyError
