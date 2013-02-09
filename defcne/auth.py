# File: auth.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-02-08

import random
import string

from pyramid import security

from models import (
        DBSession,
        UserTickets,
        )

def current_user(request):
    """
    This is added to the request as an attribute named "user"

    The function takes care of everything and caches various results so that
    for each time we call `user_groups` we don't rerun the database queries
    unnecessarily. It is highly unlikely that in the milliseconds it takes to
    render the page that the user is going to lose access to a particular
    resource.
    """

    class UserData:
        pass
    
    def _user_nonexistent():
        udata = UserData()
        udata.username = None 
        udata.user = None
        udata.ticket = None
        udata.groups = None

        return udata

    def _user_exists(user, ticket, groups):
        udata = UserData()
        udata.username = user.username
        udata.user = user
        udata.ticket = ticket
        udata.groups = groups

        return udata

    userid = security.unauthenticated_userid(request)
    
    # Check to see if any tokens are set
    if 'REMOTE_USER_TOKENS' in request.environ:
        cur_ticket = [x for x in request.environ['REMOTE_USER_TOKENS'] if 'tkt_' in x]
        cur_ticket = cur_ticket[0][4:] if len(cur_ticket) == 1 else None

        # If we don't get a ticket, we return that the user is non-existent
        if cur_ticket is None:
            return _user_nonexistent()
      
        # Find the user by looking up the ticket/username
        ticket = UserTickets.find_ticket_username(cur_ticket, userid)
        
        # If the ticket has been removed, we unauth the user
        if ticket is None:
            return _user_nonexistent()

        user = ticket.user
       
        # Load up all the groups that the user is in
        user_groups = ['group:' + grp.name for grp in user.groups]

        # Return a valid user containing data
        return _user_exists(user, ticket, user_groups)

    return _user_nonexistent() 

def user_groups(userid, request):
    """
    Returns the users groups

    First we check to see if the user still has a valid ticket for this
    particular authentication cookie. We want to be able to log users out
    before the cookie itself has expired.

    After checking the ticket is still valid we get the users groups, and
    return those, if there are any groups to speak of.
    """

    user = request.user

    if user.user is None:
        return None

    return user.groups

def remember(request, principal, **kw):
    """
    Remember the user, and create a new session ticket

    First we create a brand new ticket, add it for the user to the database as
    a valid ticket, then we call security.remember() which does the actual work
    of creating the cookie that is going to get sent to the user.
    """

    ticket = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(128))

    user = User.find_user(principal)
    user.tickets.append(UserTickets(ticket=ticket, remote_addr=request.environ['REMOTE_ADDR'] if 'REMOTE_ADDR' in request.environ else None))

    if 'tokens' in kw:
        kw['tokens'].append('tkt_' + ticket)
    else:
        kw['tokens'] = ['tkt_' + ticket]

    print kw['tokens']

    return security.remember(request, principal, **kw)

def forget(request):
    """
    Forget the users session/ticket

    This removes the users session/ticket entirely, unsets the cookie as well
    as removing the ticket from the database.
    """
    
    user = request.user

    if user.user is None:
        return security.forget(request)

    DBSession.delete(user.ticket) 
    
    return security.forget(request)
