# File: User.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

import colander
import deform

from csrf import CSRFSchema

from ..models import (
        User,
        UserValidation,
        )

def validate_unique_username(node, value):
    if User.find_user(value) != None:
        raise colander.Invalid(node, msg='Username already exists.')

def validate_unique_email(node, value):
    if User.find_user_by_email(value) != None:
        raise colander.Invalid(node, msg='Email has previously been registered.')

class UserForm(CSRFSchema):
    """The user registration form."""
    username = colander.SchemaNode(colander.String(), title="Username", validator=validate_unique_username)
    realname = colander.SchemaNode(colander.String(), title="Name")
    email    = colander.SchemaNode(colander.String(), title="Email address", validator=colander.All(colander.Length(max=254), validate_unique_email))
    password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5),
                widget=deform.widget.CheckedPasswordWidget(size=20),
                description='Please type your password twice')


def login_username_password_matches(form, value):
    if not User.validate_user_password(value['username'], value['password']):
        exc = colander.Invalid(form, 'Username or password is incorrect')
        exc['username'] = ''
        exc['password'] = ''
        raise exc

class LoginForm(CSRFSchema):
    """The user login form."""
    username = colander.SchemaNode(colander.String(), title="Username")
    password = colander.SchemaNode(colander.String(), title="Password", validator=colander.Length(min=5), widget=deform.widget.PasswordWidget(size=20))

def validate_token_matches(form, value):
    validate = UserValidation.find_token(value['token'])
    if validate is None:
        exc = colander.Invalid(form, 'Validation token is invalid')
        exc['username'] = 'Username does not exist or is not valid for token'
        exc['token'] = 'Token is invalid'
        raise exc

    if validate.user.username != value['username']:
        exc = colander.Invalid(form, 'Validation token is invalid')
        exc['username'] = 'Username does not exist or is not valid for token'
        exc['token'] = 'Token is invalid'
        raise exc

class ValidateForm(CSRFSchema):
    """The validation form, where the user enters their token"""
    username = colander.SchemaNode(colander.String(), title="Username")
    token = colander.SchemaNode(colander.String(), title="Validation token")
