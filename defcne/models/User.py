# File: Users.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-05

from meta import Base
from meta import DBSession

from sqlalchemy import (
        Boolean,
        Column,
        ForeignKey,
        Integer,
        String,
        Table,
        Unicode,
        )

from sqlalchemy.orm import (
        relationship,
        )

class User(Base):
    __table__ = Table('users', Base.metadata,
            Column('id', Integer, primary_key=True, unique=True),
            Column('username', Unicode(128), unique=True, index=True),
            Column('realname', Unicode(256), index=True),
            Column('email', Unicode(256), unique=True, index=True),
            Column('credentials', Unicode(60)), # bcrypt
            Column('validated', Boolean, default=False),
            )

    groups = relationship("Group", secondary="user_groups", lazy="joined")

    @classmethod
    def find_user(cls, username):
        return DBSession.query(cls).filter(cls.username == username).first()

    @classmethod
    def find_user_by_email(cls, email):
        return DBSession.query(cls).filter(cls.email == email).first()

class UserValidation(Base):
    __table__ = Table('user_validation', Base.metadata,
            Column('token', Unicode(128), primary_key=True, unique=True),
            Column('user_id', Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE")),
            )

    user = relationship("User", lazy="joined")

    @classmethod
    def find_token(cls, token):
        return DBSession.query(cls).filter(cls.token == token).first()

