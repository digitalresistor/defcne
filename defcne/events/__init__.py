# Package

class UserEvents(object):
    def __init__(self, request, context, user, **kw):
        self.request = request
        self.context = context
        self.user = user
        self.kw = kw

class UserRegistered(UserEvents):
    pass

class UserForgetPassword(UserEvents):
    pass

class UserChangedPassword(UserEvents):
    pass

class ContestEventEvents(object):
    def __init__(self, request, context, cne, **kw):
        self.request = request
        self.context = context
        self.cne = cne
        self.kw = kw

class ContestEventCreated(ContestEventEvents):
    pass

class ContestEventUpdated(ContestEventEvents):
    pass


class ContestEventTicket(object):
    def __init__(self, ticket, *args, **kw):
        self.ticket = ticket
        super(ContestEventTicket, self).__init__(*args, **kw)

class ContestEventTicketCreated(ContestEventTicket):
    pass

class ContestEventTicketUpdated(ContestEventTicket):
    pass

