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

class CVEEvents(object):
    def __init__(self, request, context, cne, **kw):
        self.request = request
        self.context = context
        self.cne = cne
        self.kw = kw

class CVECreated(CVEEvents):
    pass

class CVEUpdated(CVEEvents):
    pass

class CVETicket(CVEEvents):
    def __init__(self, ticket, *args, **kw):
        self.ticket = ticket
        super(ContestEventTicket, self).__init__(*args, **kw)

class CVETicketCreated(CVETicket):
    pass

class CVETicketUpdated(CVETicket):
    pass

