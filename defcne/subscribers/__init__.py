# Package

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from .. import models as m

__user_created__ = """DEFCnE Account Validation

Sorry, slight detour, just want to make sure you can receive emails from us!

{validate_url}

If you can't click the link, you can use the following information instead:

url: {validate_url_nodata}
username: {username}
token: {token}

Thanks,
DEFCnE Team"""

def user_created(event):
    # Send the user an email with the new link

    text = __user_created__.format(validate_url=event.kw['validate_url'], validate_url_nodata=event.request.route_url('defcne.user', traverse=('validate')), username=event.user.disp_uname, token=event.kw['token'])
    message = Message(subject="DEFCnE User Account Validation", sender="defcne@defcne.net", recipients=[event.user.email], body=text)
    get_mailer(event.request).send(message)


__user_forgotpassword__ = """DEFCnE Reset Account

You, or someone claiming to be you has requested to reset the password on your
account. If you did not request a password reset you may safely ignore this
email, otherwise the link below will take you to the password reset:

{reset_url}

If you can't click the link, you can use the following information instead:

url: {reset_url_nodata}
username: {username}
token: {token}
 
Thanks,
DEFCnE Team"""

def user_forgotpassword(event):
    # Sent the user an email with the reset link

    text = __user_forgotpassword__.format(reset_url=event.kw['reset_url'], reset_url_nodata=event.request.route_url('defcne.user', traverse=('reset')), username=event.user.disp_uname, token=event.kw['token'])
    message = Message(subject="DEFCnE Reset Account", sender="defcne@defcne.net", recipients=[event.user.email], body=text)
    get_mailer(event.request).send(message)


__user_passwordupdated__ = """DEFCnE Password Updated

You, hopefully, changed your password. If you have not changed your password,
your account was most likely compromised.

If you think your account may have been compromised, reset your password and
change it!

Thanks,
DEFCnE Team"""

def user_passwordupdated(event):
    # Send the user an email when their password is updated

    text = __user_passwordupdated__
    message = Message(subject="DEFCnE Password Updated", sender="defcne@defcne.net", recipients=[event.user.email], body=text)
    get_mailer(event.request).send(message)

__staff_eventcreated__ = """DEFCnE Contest/Event Created

A new contest event: "{contest_name}" has been created by "{contest_owner}".

You can manage the event by going to:

{event_manage_url}

You'll want to make sure you are logged in before attempting to access the above URL.

Cheers,
DEFCnE's Little Helper Bot
"""

def cne_created(event):
    manage_url = event.request.route_url('defcne.e', traverse=(event.cne.dc, event.cne.id, 'manage'))
    text = __staff_eventcreated__.format(contest_name=event.cne.disp_name, contest_owner=event.request.user.user.disp_uname, event_manage_url=manage_url)

    staff_list = m.Group.find_group(u'staff').users
    staff_emails = [user.email for user in staff_list]

    message = Message(subject="DEFCnE Contest/Event Created", sender="defcne@defcne.net", recipients=staff_emails, body=text)
    get_mailer(event.request).send(message)

def cne_updated(event):
    pass
