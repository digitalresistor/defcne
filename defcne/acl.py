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

import models as m

class FakeRoot(object):
    __name__ = None
    __parent__ = None

# The traversal for /user/

class User(object):
    __name__ = 'user'
    __parent__ = FakeRoot()
    __acl__ = [
                (Allow, Authenticated, 'view'),
                (Allow, Authenticated, 'edit'),
              ]

    def __init__(self, request):
        pass

    def __getitem__(self, key):
        raise KeyError

# The traversal for /u/

class Usernames(object):
    __name__ = 'users'
    __parent__ = FakeRoot()
    __acl__ = []

    def __init__(self, request):
        pass

    def __getitem__(self, key):
        user = m.User.find_user(key)

        if user is None:
            raise KeyError

        item = Username(user)
        item.__parent__ = self
        return item

class Username(object):
    def __init__(self, user):
        self.user = user
        self.__name__ = user.username

    def __getitem__(self, key):
        raise KeyError

# The traversal for /events/

class Events(object):
    __name__ = 'events'
    __parent__ = FakeRoot()
    __acl__ = [
                (Allow, "group:adminstrators", ALL_PERMISSIONS),
                (Allow, Authenticated, 'create'),
            ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        try:
            dc = int(key)
            item = DefconEvent(dc)

            item.__parent__ = self

            return item

        except ValueError:
            raise KeyError

class DefconEvent(object):
    def __init__(self, dc):
        self.__name__ = dc
        self.dc = dc

    def __getitem__(self, key):
        try:
            eid = int(key)
        except ValueError:
            return None

        event = m.DBSession.query(m.Event).get(eid)

        if event is None:
            return None
        else:
            item = Event(event)
            item.__parent__ = self

            return item

class Event(object):
    @property
    def __acl__(self):
        acl = [
                (Allow, "group:administrators", ALL_PERMISSIONS),
                (Allow, "group:staff", 'edit'),
                (Allow, "group:staff", 'view'),
                (Allow, "group:staff", 'manage'),
                (Allow, "userid:{id}".format(id=self.event.owner.id), ('edit', 'view', 'manage')),
                ]

        if self.event.status == 5:
            acl.append((Allow, Everyone, 'view'))

        return acl

    def __init__(self, event):
        self.event = event
        self.__name__ = event.id

    def __getitem__(self, key):
        raise KeyError

# The traversal for /contests/

class Contests(object):
    __name__ = 'contests'
    __parent__ = FakeRoot()
    __acl__ = [
                (Allow, "group:adminstrators", ALL_PERMISSIONS),
                (Allow, Authenticated, 'create'),
            ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        try:
            dc = int(key)
            item = DefconContest(dc)

            item.__parent__ = self

            return item

        except ValueError:
            raise KeyError

class DefconContest(object):
    def __init__(self, dc):
        self.__name__ = dc
        self.dc = dc

    def __getitem__(self, key):
        try:
            cid = int(key)
        except ValueError:
            return None

        contest = m.DBSession.query(m.Contest).get(cid)

        if contest is None:
            return None
        else:
            item = Contest(contest)
            item.__parent__ = self

            return item

class Contest(object):
    @property
    def __acl__(self):
        acl = [
                (Allow, "group:administrators", ALL_PERMISSIONS),
                (Allow, "group:staff", 'edit'),
                (Allow, "group:staff", 'view'),
                (Allow, "group:staff", 'manage'),
                (Allow, "userid:{id}".format(id=self.contest.owner.id), ('edit', 'view', 'manage')),
                ]

        if self.contest.status == 5:
            acl.append((Allow, Everyone, 'view'))

        return acl

    def __init__(self, contest):
        self.contest = contest
        self.__name__ = contest.id

    def __getitem__(self, key):
        raise KeyError


class Badges(object):
    def __init__(self):
        pass

# The traversal for /magic/

class Magic(object):
    __name__ = 'magic'
    __parent__ = FakeRoot()
    __acl__ = [
                (Allow, 'group:administrators', ALL_PERMISSIONS),
                (Allow, "group:staff", 'magic'),
              ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        item = None

        if key == 'events':
            item = Events(self.request)

        if key == 'contests':
            item = Contests(self.request)

        if key == 'users':
            item = Usernames(self.request)

        if key == 'badges':
            item = Badges()

        if item is None:
            raise KeyError

        item.__parent__ = self

        return item

