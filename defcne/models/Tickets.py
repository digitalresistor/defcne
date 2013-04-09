# File: Tickets.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-04-09

import datetime

from meta import Base
from meta import DBSession

from sqlalchemy import (
        Column,
        DateTime,
        ForeignKey,
        Integer,
        Table,
        Unicode,
        text,
        func,
        )

from sqlalchemy.orm import (
        relationship,
        )

class Ticket(Base):
    __table__ = Table('tickets', Base.metadata,
            Column('id', Integer, primary_key=True, unique=True),
            Column('event', Integer, ForeignKey('events.id', onupdate='CASCADE', ondelete='CASCADE')),
            Column('userid', Integer, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE')),
            Column('ticket', Unicode),
            Column('created', DateTime, server_default=text('current_timestamp')),
            )
    
    user = relationship("User")

    @classmethod
    def count_event_tickets(cls, event_id):
        return DBSession.query(func.count(cls.id)).filter(cls.event == event_id).all()

    @classmethod
    def find_event_tickets(cls, event_id):
        return DBSession.query(cls).filter(cls.event == event_id).order_by(cls.created.asc()).all()
