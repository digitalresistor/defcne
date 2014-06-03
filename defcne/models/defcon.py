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
        contains_eager,
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
        l = DBSession.query(cls).filter(cls.id == num).join(cls.cve).filter(CVEBase.type == 'event').options(contains_eager('cve')).all()

        if len(l) == 0:
            return None

        return l[0]

    @classmethod
    def find_defcon_contests(cls, num):
        l = DBSession.query(cls).filter(cls.id == num).join(cls.cve).filter(CVEBase.type == 'contest').options(contains_eager('cve')).all()

        if len(l) == 0:
            return None

        return l[0]

    @classmethod
    def find_defcon_villages(cls, num):
        l = DBSession.query(cls).filter(cls.id == num).join(cls.cve).filter(CVEBase.type == 'village').options(contains_eager('cve')).all()

        if len(l) == 0:
            return None

        return l[0]


