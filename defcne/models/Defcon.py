# File: Defcon.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-07

from meta import Base, DBSession

from sqlalchemy import (
        Column,
        Integer,
        String,
        Table,
        Unicode,
        )

from sqlalchemy.orm import (
        relationship,
        eagerload,
        )

class Defcon(Base):
    __table__ = Table('defcon', Base.metadata,
            Column('id', Integer, primary_key=True, unique=True, autoincrement=False),
            Column('url', Unicode(256), index=True),
            )

    events = relationship("Event", secondary="defcon_events", lazy="noload")

    @classmethod
    def find_defcon(cls, num):
        return DBSession.query(cls).filter(cls.id == num).first()

    @classmethod
    def find_defcon_events(cls, num):
        return DBSession.query(cls).filter(cls.id == num).options(eagerload('events')).first()

