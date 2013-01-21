# File: Users.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-05

from meta import Base

from sqlalchemy import (
        Column,
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
            Column('credentials', Unicode(60)), # bcrypt
            )

    groups = relationship("Group", secondary="user_groups", lazy="joined")

