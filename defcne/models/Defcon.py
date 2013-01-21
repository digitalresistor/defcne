# File: Defcon.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-07

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

class Defcon(Base):
    __table__ = Table('defcon', Base.metadata,
            Column('id', Integer, primary_key=True, unique=True, autoincrement=False),
            Column('url', Unicode(256), index=True),
            )

