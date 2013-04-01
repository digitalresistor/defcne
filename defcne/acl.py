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
    __acl__ = [
                (Allow, Authenticated, 'view'),
                (Allow, Authenticated, 'edit'),
              ]

    def __init__(self, request):
        pass

    def __getitem__(self, key):
        raise KeyError

# The traversal for /e/

class Events(object):
    __acl__ = [
                (Allow, Authenticated, 'authenticated'),
            ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        try:
            dc = int(key)
            return DefconEvent(self, dc)

        except ValueError:
            raise KeyError

class DefconEvent(object):
    def __init__(self, events, dc):
        self.__parent__ = events
        self.__name__ = dc
        self.dc = dc

    def __getitem__(self, key):
        return Event(self, key)

class Event(object):
    def __init__(self, dc, name):
        self.__parent__ = self.dc = dc
        self.__name__ = self.name = name

    def __getitem__(self, key):
        raise KeyError

# The traversal for /magic/

class Magic(object):
    __acl__ = [
                (Allow, 'group:administrators', 'view'),
                (Allow, 'group:administrators', 'edit'),
                (Allow, 'group:staff', 'view'),
                (Allow, 'group:staff', 'edit'),
              ]

    def __init__(self, request):
        pass

    def __getitem__(self, key):
        raise KeyError

