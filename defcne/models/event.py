# File: Event.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-03-09

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
        UnicodeText,
        and_,
        )

from sqlalchemy.orm import (
        contains_eager,
        noload,
        relationship,
        )

from sqlalchemy.ext.hybrid import hybrid_property
from cvebase import CVEBase


class EventSpace(Base):
    __table__ = Table('event_space', Base.metadata,
            Column('event_id', Integer, ForeignKey('events.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
            Column('tables', Integer),
            Column('chairs', Integer),
            Column('stage', Boolean),
            Column('location', UnicodeText),
            Column('mobilebar', UnicodeText),
            )

    def from_appstruct(self, appstruct):
        self.tables = appstruct['tables']
        self.chairs = appstruct['chairs']
        self.stage = appstruct['stage']
        self.location = appstruct['location']
        self.mobilebar = appstruct['mobilebar']

    def to_appstruct(self):
        return {
                'event_id': self.event_id,
                'tables': self.tables,
                'chairs': self.chairs,
                'stage': self.stage,
                'location': self.location,
                'mobilebar': self.mobilebar,
                }


class Event(CVEBase):
    __table__ = Table('events', Base.metadata,
            Column('id', Integer, ForeignKey('cve.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
            Column('onsite', Boolean),
            Column('official', Boolean),
            Column('security', Boolean),
            Column('signage', UnicodeText),
            )
    __mapper_args__ = {
                'polymorphic_identity': 'event',
            }

    space = relationship("EventSpace", uselist=False)

    def from_appstruct(self, appstruct):
        super(Event, self).from_appstruct(appstruct)

        self.onsite = appstruct['onsite']
        self.official = appstruct['official']
        self.security = appstruct['security']
        self.signage = appstruct['signage']

        if self.onsite and self.space is None:
            self.space = EventSpace()
            self.space.from_appstruct(appstruct['space'])

        if self.onsite and self.space:
            self.space.from_appstruct(appstruct['space'])

    def to_appstruct(self):
        ret = super(Event, self).to_appstruct()

        ret.update(
                    {
                        'id': self.id,
                        'onsite': self.onsite,
                        'official': self.official,
                        'security': self.security,
                        'signage': self.signage,
                    }
                )

        if self.space is not None:
            ret.update({'space': self.space.to_appstruct()})

        return ret

