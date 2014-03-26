# File: Event.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-03-03

import colander
import deform

from pyramid_deform import SessionFileUploadTempStore
from urlparse import urlparse

from csrf import CSRFSchema

from .. import models as m
from Ticket import TicketForm

from cvebase import (
        CVEBase,
        POCS,
        AccessPoints,
        WiredInternets,
        Powers,
        )

class EventSpace(colander.Schema):
    tables = colander.SchemaNode(colander.Int(), title="Tables", default=0, description="Standard table size is 4x6")
    chairs = colander.SchemaNode(colander.Int(), title="Chairs", default=0)
    stage = colander.SchemaNode(colander.Boolean(), title="Stage", default=False, missing=False)
    location = colander.SchemaNode(colander.String(), title="Location for Event", missing='', widget=deform.widget.TextAreaWidget(rows=5, cols=60))
    mobilebar = colander.SchemaNode(colander.String(), title="Mobile Bar", description="Do you require a mobile bar?", missing='', widget=deform.widget.TextAreaWidget(rows=5, cols=60))


class EventForm(CVEBase):
    """The Event registration form ... """

    onsite = colander.SchemaNode(colander.Boolean(), title="Onsite Event", description="Onsite events are held at the location where DEF CON is. If you are on-site, please fill out the Onsite Space Requirements.")
    official = colander.SchemaNode(colander.Boolean(), title="Official event", description="Would this be an official event that would be supported and backed by DEF CON, or is this considered unofficial.")
    security = colander.SchemaNode(colander.Boolean(), title="Security", description="Does your event require DEF CON security to be present? This is available only to onsite events.")
    signage = colander.SchemaNode(colander.String(), title="Signage", description="What banners/advertisements are you bringing to make people aware of your event", widget=deform.widget.TextAreaWidget(rows=5, cols=60))

    space = EventSpace(title="Onsite Space Requirements")

    ticket = colander.SchemaNode(colander.String(), title="Extra Requests", widget=deform.widget.TextAreaWidget(rows=5, cols=60), missing=unicode(''))



