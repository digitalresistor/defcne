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
        UniqueConstraint,
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

status_types = {
        0: u'Pending',
        1: u'Under Review',
        2: u'More Information Requested',
        3: u'Rejected',
        4: u'Accepted',
        5: u'Published',
        }

badge_types = {
        0: u'Human',
        1: u'Contest and Events',
        2: u'Other',
        }


class CVEBase(Base):
    __table__ = Table('cve', Base.metadata,
            Column('id', Integer, primary_key=True, unique=True),
            Column('dc', Integer, ForeignKey('defcon.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('type', Unicode(50), nullable=False),
            Column('name', Unicode, nullable=False, index=True),
            Column('disp_name', Unicode),
            Column('oneliner', Unicode),
            Column('description', UnicodeText),
            Column('website', Unicode),
            Column('logo', String),
            Column('user_id', Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
            Column('status', Integer, default=0),

            UniqueConstraint('dc', 'type', 'name'),
            )

    CheckConstraint(__table__.c.status.in_(status_types.keys()))

    __mapper_args__ = {
                'polymorphic_identity': 'cve',
                'polymorphic_on': __table__.c.type,
            }

    owner = relationship("User")
    pocs = relationship("POC")
    tickets = relationship("Ticket")

    _name = __table__.c.name

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self.disp_name = value
        self._name = value.lower()

    def from_appstruct(self, appstruct):
        if 'id' in appstruct:
            if appstruct['id'] != self.id:
                print "ID in appstruct does not match: {} - {}".format(type(appstruct['id']), type(self.id))
                raise ValueError

        if 'dc' in appstruct:
            self.dc = appstruct['dc']

        self.name = appstruct['name']
        self.oneliner = appstruct['oneliner']
        self.description = appstruct['description']
        self.website = appstruct['website']

        if 'logo_path' in appstruct:
            self.logo = appstruct['logo_path']

        new_poc_ids = set([p['id'] for p in appstruct['pocs'] if p['id'] != -1])
        cur_poc_ids = set([p.id for p in self.pocs])
        del_poc_ids = cur_poc_ids - new_poc_ids

        if len(del_poc_ids):
            for poc in self.pocs:
                if poc.id in del_poc_ids:
                    DBSession.delete(poc)

        for poc in appstruct['pocs']:
            if poc['id'] in cur_poc_ids:
                cur_poc = [p for p in self.pocs if p.id == poc['id']][0]
                cur_poc.from_appstruct(poc)
            else:
                npoc = POC()
                npoc.from_appstruct(poc)
                self.pocs.append(npoc)


    def to_appstruct(self):
        return {
                'id': self.id,
                'dc': self.dc,
                'name': self.name,
                'disp_name': self.disp_name,
                'oneliner': self.oneliner,
                'description': self.description,
                'website': self.website,
                'logo': self.logo,
                'status': self.status,
                'pocs': [poc.to_appstruct() for poc in self.pocs]
                }

    @classmethod
    def find(cls, type, value):
        return DBSession.query(cls).filter(cls.type == type, cls.name == value.lower()).first()


class POC(Base):
    __table__ = Table('cve_pocs', Base.metadata,
            Column('cve_id', Integer, ForeignKey('cve.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('id', Integer, primary_key=True, unique=True),
            Column('name', Unicode),
            Column('email', Unicode),
            Column('cellphone', Unicode),
            )

    def from_appstruct(self, appstruct):
        self.name = appstruct['name']
        self.email = appstruct['email']
        self.cellphone = appstruct['cellphone']

    def to_appstruct(self):
        return {
                'cve_id': self.cve_id,
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'cellphone': self.cellphone,
                }


class Power(Base):
    __table__ = Table('cve_power', Base.metadata,
            Column('cve_id', Integer, ForeignKey('cve.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('id', Integer, primary_key=True, unique=True),
            Column('outlets', Integer),
            Column('justification', Unicode),
            Column('threephase', Boolean),
            )

    def from_appstruct(self, appstruct):
        self.outlets = appstruct['outlets']
        self.justification = appstruct['justification']
        self.threephase = appstruct['threephase']

    def to_appstruct(self):
        return {
                'cve_id': self.cve_id,
                'id': self.id,
                'outlets': self.outlets,
                'justification': self.justification,
                'threephase': self.threephase,
                }

class WiredInternet(Base):
    __table__ = Table('cve_wiredinternet', Base.metadata,
            Column('cve_id', Integer, ForeignKey('cve.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('id', Integer, primary_key=True, unique=True),
            Column('justification', Unicode),
            )

    def from_appstruct(self, appstruct):
        self.justification = appstruct['justification']

    def to_appstruct(self):
        return {
                'cve_id': self.cve_id,
                'id': self.id,
                'justification': self.justification,
                }


class AccessPoint(Base):
    __table__ = Table('cve_accesspoint', Base.metadata,
            Column('cve_id', Integer, ForeignKey('cve.id', onupdate="CASCADE", ondelete="CASCADE")),
            Column('id', Integer, primary_key=True, unique=True),
            Column('hwmac', Unicode),
            Column('apbrand', Unicode),
            Column('ssid', Unicode),
            )

    def from_appstruct(self, appstruct):
        self.hwmac = appstruct['hwmac']
        self.apbrand = appstruct['apbrand']
        self.ssid = appstruct['ssid']

    def to_appstruct(self):
        return {
                'cve_id': self.cve_id,
                'id': self.id,
                'hwmac': self.hwmac,
                'apbrand': self.apbrand,
                'ssid': self.ssid,
                }


class Badges(Base):
    __table__ = Table('cve_badges', Base.metadata,
            Column('cve_id', Integer, ForeignKey('cve.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
            Column('id', Integer, primary_key=True, unique=True),
            Column('type', Integer),
            Column('amount', Integer),
            Column('reason', Unicode),
            )
    CheckConstraint(__table__.c.type.in_(badge_types.keys()))

    def from_appstruct(self, appstruct):
        self.type = appstruct['type']
        self.amount = appstruct['amount']
        self.reason  = appstruct['reason']

    def to_appstruct(self):
        return {
                'cve_id': self.cve_id,
                'id': self.id,
                'type': self.type,
                'amount': self.amount,
                'reason': self.reason,
                }
