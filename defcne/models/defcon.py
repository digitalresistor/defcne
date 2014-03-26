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

from cvebase import CVEBase

class Defcon(Base):
    __table__ = Table('defcon', Base.metadata,
            Column('id', Integer, primary_key=True, unique=True, autoincrement=False),
            Column('url', Unicode(256), index=True),
            )

    cve = relationship("CVEBase", lazy="noload")

    @classmethod
    def find_defcon(cls, num):
        return DBSession.query(cls).filter(cls.id == num).first()

    @classmethod
    def find_defcon_events(cls, num):
        return DBSession.query(cls).filter(cls.id == num).filter(CVEBase.type == 'event').options(eagerload('cve')).first()

    @classmethod
    def find_defcon_contests(cls, num):
        return DBSession.query(cls).filter(cls.id == num).filter(CVEBase.type == 'contest').options(eagerload('cve')).first()

    @classmethod
    def find_defcon_villages(cls, num):
        return DBSession.query(cls).filter(cls.id == num).filter(CVEBase.type == 'village').options(eagerload('cve')).first()

