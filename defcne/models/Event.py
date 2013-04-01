# File: Event.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-03-09

import datetime

from meta import Base
from meta import DBSession

from sqlalchemy import (
        Boolean,
        CheckConstraint,
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

status_types = {
        0: 'Pending',
        1: 'Under Review',
        2: 'More Information Requested',
        3: 'Rejected',
        4: 'Accepted',
        5: 'Published',
        }

class Event(Base):
    __table__ = Table('events', Base.metadata,
            Column('id', Integer, primary_key=True, unique=True),
            Column('name', Unicode, unique=True, nullable=False),
            Column('disp_name', Unicode),
            Column('shortname', Unicode, unique=True, nullable=False),
            Column('description', Unicode),
            Column('website', Unicode),
            Column('logo', String),
            Column('hrsofoperation', Unicode),
            Column('tables', Integer),
            Column('chairs', Integer),
            Column('represent', Unicode),
            Column('numparticipants', Integer),
            Column('blackbadge', Boolean, default=False),
            Column('status', Integer, default=0),
            )
    CheckConstraint(__table__.c.status.in_(status_types.keys()))

    pocs = relationship("EventPOC", lazy="noload")
    power = relationship("EventPower", lazy="noload")
    drops = relationship("EventWiredDrop", lazy="noload")
    aps = relationship("EventAP", lazy="noload")
    owner = relationship("User", secondary="user_events", lazy="join")
    dc = relationship("Defcon", secondary="defcon_events", lazy="noload")

    _name = __table__.c.name
    _shortname = __table__.c.shortname

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self.disp_name = value
        self._name = value.lower()

    @hybrid_property
    def shortname(self):
        return self._shortname

    @shortname.setter
    def shortname(self, value):
        self._shortname = value.lower()

    @classmethod
    def find_event(cls, name):
        return DBSession.query(cls).filter(cls.name == name.lower()).first()

    @classmethod
    def find_event_short(cls, name):
        return DBSession.query(cls).filter(cls.shortname == name.lower()).first()

class EventPOC(Base):
    __table__ = Table('event_pocs', Base.metadata,
            Column('event_id', Integer, ForeignKey('events.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('id', Integer, primary_key=True, unique=True),
            Column('name', Unicode),
            Column('email', Unicode),
            Column('cellphone', Unicode),
            )

class EventPower(Base):
    __table__ = Table('event_powers', Base.metadata,
            Column('event_id', Integer, ForeignKey('events.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('id', Integer, primary_key=True, unique=True),
            Column('amps', Integer),
            Column('outlets', Integer),
            Column('justification', Unicode),
            )

class EventWiredDrop(Base):
    __table__ = Table('event_drops', Base.metadata,
            Column('event_id', Integer, ForeignKey('events.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('id', Integer, primary_key=True, unique=True),
            Column('typeof', Unicode),
            Column('justification', Unicode),
            )

class EventAP(Base):
    __table__ = Table('event_aps', Base.metadata,
            Column('event_id', Integer, ForeignKey('events.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('id', Integer, primary_key=True, unique=True),
            Column('hwmac', Unicode),
            Column('apbrand', Unicode),
            Column('ssid', Unicode),
            )

class UserEvents(Base):
    __table__ = Table('user_events', Base.metadata,
            Column('userid', Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"), index=True),
            Column('eventid', Integer, ForeignKey('events.id', onupdate="CASCADE", ondelete="CASCADE"), index=True),

            PrimaryKeyConstraint('userid', 'eventid'),
            )

class DefconEvents(Base):
    __table__ = Table('defcon_events', Base.metadata,
            Column('defconid', Integer, ForeignKey('defcon.id', onupdate="CASCADE", ondelete="CASCADE"), index=True),
            Column('eventid', Integer, ForeignKey('events.id', onupdate="CASCADE", ondelete="CASCADE"), index=True),

            PrimaryKeyConstraint('defconid', 'eventid'),
            )
