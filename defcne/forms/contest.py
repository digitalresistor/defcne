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

class ContestForm(CVEBase):
    """The Event registration form ... """

    hrsofoperation = colander.SchemaNode(colander.String(), title="Hours of Operation", description="Your requested hours of operation! (Contests area open from 09:00 till 17:00)", missing=unicode(''), widget=deform.widget.TextAreaWidget(rows=10, cols=60))
    power = Powers(title="Power required", default=list())
    spacereq = colander.SchemaNode(colander.String(), title="Space Requirements", description="How much space does your contest require? (10x10, 10x20, 20x20, other)", default="10x10")
    tables = colander.SchemaNode(colander.Int(), title="Tables", default=0)
    chairs = colander.SchemaNode(colander.Int(), title="Chairs", default=0)
    signage = colander.SchemaNode(colander.String(), title="Signage", description="What signage are you bringing for your contest")
    projectors = colander.SchemaNode(colander.Int(), title="Projectors", default=0)
    screens = colander.SchemaNode(colander.Int(), title="Screens", default=0)
    drops = WiredInternets(title="Wired access", description="If you need wired access to the DEF CON network let us know.", default=list())
    aps = AccessPoints(title="Wireless AP", description="If you require your own wireless access point (we don't provide hardware), we need the details to give on to the DEF CON NOC", default=list())
    represent = colander.SchemaNode(colander.String(), title="Representation", description="Who will be representing this contest/event on stage. Black badge events will be at DEF CON closing ceremonies, non-black badge events will be at CnE closing ceremonies. You will be notified if you are a black badge event or not.")
    numparticipants = colander.SchemaNode(colander.Int(), title="Number of Participants", description="This is a rough estimate of the expected number of participants.", default=0)
    years = colander.SchemaNode(colander.Int(), title="Years Ran", description="How many years has this contest been run previously?", default=0)
    #otherrequests = TicketForm(title="Extra Requests:")




