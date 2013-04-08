# Package

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

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

def user_forgotpassword(event):
    pass

def user_passwordupdated(event):
    pass

def cne_created(event):
    pass

def cne_updated(event):
    pass
