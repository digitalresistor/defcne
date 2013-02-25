# File: Users.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-05

import datetime

from meta import Base
from meta import DBSession

from sqlalchemy import (
        Boolean,
        Column,
        DateTime,
        ForeignKey,
        Index,
        Integer,
        PrimaryKeyConstraint,
        String,
        Table,
        Unicode,
        and_,
        )

from sqlalchemy.orm import (
        contains_eager,
        noload,
        relationship,
        )

from sqlalchemy.ext.hybrid import hybrid_property

from cryptacular.bcrypt import BCRYPTPasswordManager

class User(Base):
    __table__ = Table('users', Base.metadata,
            Column('id', Integer, primary_key=True, unique=True),
            Column('username', Unicode(128), unique=True, index=True),
            Column('disp_uname', Unicode(128)), # The users display username. We cache the lowered username in username.
            Column('realname', Unicode(256), index=True),
            Column('email', Unicode(256), unique=True, index=True),
            Column('credentials', String(60)), # bcrypt
            Column('validated', Boolean, default=False),
            )

    groups = relationship("Group", secondary="user_groups", lazy="joined")
    tickets = relationship("UserTickets", lazy="noload")

    _username = __table__.c.username
    _email = __table__.c.email
    _credentials = __table__.c.credentials

    @hybrid_property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self.disp_uname = value
        self._username = value.lower()

    @hybrid_property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value.lower()

    @hybrid_property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self, value):
        manager = BCRYPTPasswordManager()
        self._credentials = manager.encode(value, rounds=12)

    @classmethod
    def find_user(cls, username):
        return DBSession.query(cls).filter(cls.username == username.lower()).first()

    @classmethod
    def find_user_no_groups(cls, username):
        return DBSession.query(cls).options(noload(cls.groups)).filter(cls.username == username.lower()).first()

    @classmethod
    def find_user_by_email(cls, email):
        return DBSession.query(cls).filter(cls.email == email.lower()).first()

    @classmethod
    def validate_user_password(cls, username, password):
        user = DBSession.query(cls).options(noload(cls.groups)).filter(cls.username == username.lower()).first()

        if user is None:
            return None

        manager = BCRYPTPasswordManager()
        if manager.check(user.credentials, password):
            return user

        return None

class UserValidation(Base):
    __table__ = Table('user_validation', Base.metadata,
            Column('token', Unicode(128)),
            Column('user_id', Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE")),

            PrimaryKeyConstraint('token', 'user_id'),
            Index('ix_uv_token_userid', 'token', 'user_id'),
            )

    user = relationship("User", lazy="joined")

    @classmethod
    def find_token_username(cls, token, username):
        return DBSession.query(cls).join(User, and_(User.username == username.lower(), User.id == cls.user_id)).filter(cls.token == token).options(contains_eager('user')).first()

            )

    user = relationship("User", lazy="joined")

    @classmethod
    def find_token_username(cls, token, username):
        return DBSession.query(cls).join(User, and_(User.username == username.lower(), User.id == cls.user_id)).filter(cls.token == token).options(contains_eager('user')).first()

class UserTickets(Base):
    __table__ = Table('user_tickets', Base.metadata,
            Column('ticket', String(128)),
            Column('user_id', Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('remote_addr', String(45)),
            Column('created', DateTime, default=datetime.datetime.utcnow, nullable=False),

            PrimaryKeyConstraint('ticket', 'user_id'),
            Index('ix_ticket_userid', 'ticket', 'user_id'),
            )

    user = relationship("User", lazy="joined")

    @classmethod
    def find_ticket_username(cls, ticket, username):
        return DBSession.query(cls).join(User, and_(User.username == username.lower(), User.id == cls.user_id)).filter(cls.ticket == ticket).options(contains_eager('user')).first()

