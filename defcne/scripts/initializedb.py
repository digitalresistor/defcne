import os
import sys
import transaction
import datetime

from sqlalchemy import engine_from_config
from sqlalchemy.exc import IntegrityError

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import *

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


defaults = {
        'groups': [
            (u'event_owners', u'Event owners'),
            (u'event_staff', u'Event staff'),
            (u'goons', u'Defcon Contests and Events goons'),
            (u'staff', u'Defcon staff'),
            (u'administrators', u'Site administrators')
            ]
        }

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    with transaction.manager:
        for (kw, items) in defaults.items():
            if kw == 'groups':
                for (name, desc) in items:
                    try:
                        group = Group(name=name, description=desc)
                        DBSession.add(group)
                        DBSession.flush()
                    except IntegrityError, e:
                        DBSession.rollback()
                        print 'Group "{name}" already exists.'.format(name=name)


