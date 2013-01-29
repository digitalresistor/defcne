# File: User.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

import colander
import deform

from csrf import CSRFSchema

from ..models import User

def validate_unique_username(node, value):
    if User.find_user(value) != None:
        raise colander.Invalid(node, msg='Username already exists.')

class UserForm(CSRFSchema):
    """The user registration form."""
    username = colander.SchemaNode(colander.String(), title="Username", validator=validate_unique_username)
    realname = colander.SchemaNode(colander.String(), title="Name")
    email    = colander.SchemaNode(colander.String(), title="Email address", validator=colander.Length(max=254))
    password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5),
                widget=deform.widget.CheckedPasswordWidget(size=20),
                description='Please type your password twice')
