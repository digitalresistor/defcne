# File: User.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

import colander
import deform

from csrf import CSRFSchema

from ..models import (
        User,
        UserValidation,
        UserForgot,
        )

from .. import models as m

@colander.deferred
def deferred_username_default(node, kw):
    request = kw.get('request')
    if request.user is None:
        print "No user found ..."
        raise ValueError('No user is logged in ...')
    return request.user.username

@colander.deferred
def deferred_username_validator(node, kw):
    def validate_username(node, value):
        request = kw.get('request')
        if request.user is None:
            raise ValueError('No user is logged in ...')
        if value != request.user.username:
            raise ValueError('Username does not match current logged in user ...')
    return validate_username

def validate_unique_username(node, value):
    if User.find_user(value) != None:
        raise colander.Invalid(node, msg='Username already exists.')

def validate_unique_email(node, value):
    if User.find_user_by_email(value) != None:
        raise colander.Invalid(node, msg='Email has previously been registered.')

class UserForm(CSRFSchema):
    """The user registration form."""
    username = colander.SchemaNode(colander.String(), title="Username", validator=validate_unique_username)
    realname = colander.SchemaNode(colander.String(), title="Name", missing=unicode(''))
    email    = colander.SchemaNode(colander.String(), title="Email address", validator=colander.All(colander.Length(max=254), validate_unique_email))
    password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5),
                widget=deform.widget.CheckedPasswordWidget(size=20),
                description='Please type your password twice')


def login_username_password_matches(form, value):
    user = User.validate_user_password(value['username'], value['password'])
    if not user:
        exc = colander.Invalid(form, 'Username or password is incorrect')
        exc['username'] = ''
        exc['password'] = ''
        raise exc

    # Normalize username
    value['username'] = user.username
    value['_internal'] = {}
    value['_internal']['user'] = user

class LoginForm(CSRFSchema):
    """The user login form."""
    username = colander.SchemaNode(colander.String(), title="Username")
    password = colander.SchemaNode(colander.String(), title="Password", validator=colander.Length(min=5), widget=deform.widget.PasswordWidget(size=20))

def lost_password_username_email_matches(form, value):
    user = User.find_user(value['username'])

    exc = colander.Invalid(form, "Username and email do not match")
    exc['username'] = ''
    exc['email'] = ''
    if user is None:
        raise exc

    if user.email != value['email']:
        raise exc

    value['_internal'] = {}
    value['_internal']['user'] = user

class LostPassword(CSRFSchema):
    username = colander.SchemaNode(colander.String(), title="Username")
    email    = colander.SchemaNode(colander.String(), title="Email address", validator=colander.Length(max=254))

def username_password_matches(form, value):
    if 'password' not in value:
        user = user.find_user(value['username'])
        if not user:
            exc = colander.Invalid(form, 'Username not found')
            raise exc
    else:
        user = User.validate_user_password(value['username'], value['password'])
        if not user:
            exc = colander.Invalid(form, 'Username or password is incorrect')
            exc['username'] = ''
            exc['password'] = ''
            raise exc

    # Normalize username
    value['username'] = user.username
    value['_internal'] = {}
    value['_internal']['user'] = user

class SetPassword(CSRFSchema):
    username = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget(), default=deferred_username_default, validator=deferred_username_validator)
    password = colander.SchemaNode(colander.String(), title="Current password", validator=colander.Length(min=5), widget=deform.widget.PasswordWidget(size=20), description='Please enter your current password')
    new_password = colander.SchemaNode(colander.String(), title="New password", validator=colander.Length(min=5), widget=deform.widget.CheckedPasswordWidget(size=20), description='Please enter your desired password, twice')

def validate_token_matches(form, value):
    validate = UserValidation.find_token_username(value['token'], value['username'])
    if validate is None:
        exc = colander.Invalid(form, 'Validation token is invalid')
        exc['username'] = 'Username does not exist or is not valid for token'
        exc['token'] = 'Token is invalid'
        raise exc

    value['_internal'] = {}
    value['_internal']['user'] = validate.user
    value['_internal']['validation'] = validate

class ValidateForm(CSRFSchema):
    """The validation form, where the user enters their token"""
    username = colander.SchemaNode(colander.String(), title="Username")
    token = colander.SchemaNode(colander.String(), title="Validation token")

def reset_token_matches(form, value):
    exc = colander.Invalid(form, 'Reset token is invalid')
    exc['username'] = 'Username does not exist or is not valid for token'
    exc['token'] = 'Token is invalid'

    userforgot = UserForgot.find_token_username(value['token'], value['username'])

    if userforgot is None:
        raise exc

    if userforgot.user.credreset is False:
        raise exc

    value['_internal'] = {}
    value['_internal']['user'] = userforgot.user
    value['_internal']['userforgot'] = userforgot

class ResetForm(CSRFSchema):
    """The validation form, where the user enters their token"""
    username = colander.SchemaNode(colander.String(), title="Username")
    token = colander.SchemaNode(colander.String(), title="Reset token")

@colander.deferred
def deferred_group_select(node, kw):
    groups = m.DBSession.query(m.Group).all();
    choices = [(x.id, '{} - {}'.format(x.name, x.description)) for x in groups]
    return deform.widget.SelectWidget(values=choices)

class Group(colander.Schema):
    group_id = colander.SchemaNode(colander.Int(), title="", default=0, missing=0, widget=deferred_group_select, description="The group the user is a part of.")

class Groups(colander.SequenceSchema):
    group = Group(title="Group")

class MagicUserEdit(CSRFSchema):
    groups = Groups()
    validated = colander.SchemaNode(colander.Bool(), title="Validated", default=True, description="User is validated (email has been verified)")

