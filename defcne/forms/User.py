# File: User.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

import colander
import deform

from csrf import CSRFSchema

class UserForm(CSRFSchema):
    """The user registration form."""
    username = colander.SchemaNode(colander.String(), title="User name")
    realname = colander.SchemaNode(colander.String(), title="Name")
    password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5),
                widget=deform.widget.CheckedPasswordWidget(size=20),
                description='Please type your password twice')
