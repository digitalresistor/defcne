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

class EventForm(CVEBase):
    """The Event registration form ... """

    onsite = colander.SchemaNode(colander.Boolean(), title="Onsite Event", description="Onsite events are held at the location where DEF CON is.")
    official = colander.SchemaNode(colander.Boolean(), title="Official event", description="Would this be an official event that would be supported and backed by DEF CON, or is this considered unofficial.")
    security = colander.SchemaNode(colander.Boolean(), title="Security", description="Does your event require DEF CON security to be present? This is available only to onsite events.")
    signage = colander.SchemaNode(colander.String(), title="Signage", description="What banners/advertisements are you bringing to make people aware of your event")

    #otherrequests = TicketForm(title="Extra Requests:")



