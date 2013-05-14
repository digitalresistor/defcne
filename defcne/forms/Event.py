# File: Event.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-03-03

import colander
import deform

from pyramid_deform import SessionFileUploadTempStore
from urlparse import urlparse

from csrf import CSRFSchema

from .. import models as m
from ..models.Event import (
        status_types,
        badge_types,
        )

from Ticket import TicketForm

@colander.deferred
def upload_widget(node, kw):
    request = kw['request']
    tmpstore = SessionFileUploadTempStore(request)
    return deform.widget.FileUploadWidget(tmpstore)

class EventPOC(colander.Schema):
    """Form that gets event point of contacts"""
    id = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget(), title="id", default=-1)
    name = colander.SchemaNode(colander.String(), title="Name")
    email = colander.SchemaNode(colander.String(), title="Email address")
    cellphone = colander.SchemaNode(colander.String(), title="Cell phone", missing=unicode(''))

class EventPOCS(colander.SequenceSchema):
    poc = EventPOC(title="Staff")

class EventPower(colander.Schema):
    id = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget(), title="id", default=-1)
    amps = colander.SchemaNode(colander.Int(), title="Amps required")
    outlets = colander.SchemaNode(colander.Int(), title="Outlets required")
    justify = colander.SchemaNode(colander.String(), title="Justification", description="Please justify your requirement.")

class EventPowers(colander.SequenceSchema):
    power = EventPower()

class EventDrop(colander.Schema):
    id = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget(), title="id", default=-1)
    typeof = colander.SchemaNode(colander.String(), title="Preferred", default='copper', widget=deform.widget.SelectWidget(values=(('copper', 'Copper'), ('fiber', 'Fiber'))), description="Choice may not be available. We will do our best!")
    justify = colander.SchemaNode(colander.String(), title="Justification", description="Please justify your requirement.")

class EventDrops(colander.SequenceSchema):
    drop = EventDrop()

class EventAP(colander.Schema):
    id = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget(), title="id", default=-1)
    hwmac = colander.SchemaNode(colander.String(), title="Wireless MAC address")
    apbrand = colander.SchemaNode(colander.String(), title="Brand Name")
    ssid = colander.SchemaNode(colander.String(), title="SSID")

class EventAPS(colander.SequenceSchema):
    ap = EventAP()

@colander.deferred
def deferred_event_verify_name_not_used(node, kw):
    def event_verify_name_not_used(node, value):
        if 'eventname' in kw:
            if kw.get('eventname') == value:
                return

        if m.Event.find_event(value) != None:
            raise colander.Invalid(node, msg='Event name already exists. Please choose another name.')
    return event_verify_name_not_used

@colander.deferred
def deferred_event_verify_shortname_not_used(node, kw):
    def event_verify_shortname_not_used(node, value):
        if ' ' in value:
            raise colander.Invalid(node, msg='Short name should not contain any spaces.')

        if 'shortname' in kw:
            if kw.get('shortname') == value:
                return

        if m.Event.find_event_short(value) != None:
            raise colander.Invalid(node, msg='Short name already exists. Please choose another name.')

    return event_verify_shortname_not_used

def event_verify_website_name(node, value):
    if value == '':
        return

    if value[0:3] == 'www':
        value = '//' + value

    result = urlparse(value, scheme='http')

    if result[0] not in ['http', 'https']:
        raise colander.Invalid(node, msg='Event website has to be an http or https address!')

    if result[1] is '':
        raise colander.Invalid(node, msg='Event website has to include a network location!')

class EventForm(CSRFSchema):
    """The Event registration form ... """
    name = colander.SchemaNode(colander.String(), title="Contest/Event Name", validator=deferred_event_verify_name_not_used)
    shortname = colander.SchemaNode(colander.String(), title="Short Name", description="A short name that doesn't include spaces. Once created, it can't be changed!", validator=deferred_event_verify_shortname_not_used)
    description = colander.SchemaNode(colander.String(), title="Description", widget=deform.widget.TextAreaWidget(rows=5, cols=60))
    website = colander.SchemaNode(colander.String(), title="Website URL", missing=unicode(''), validator=event_verify_website_name)
    logo  = colander.SchemaNode(deform.FileData(), widget = upload_widget, missing=None)
    pocs = EventPOCS(title="Event Staff", description="Other points of contact if you are not available, along with people that would be allowed access to contest/events before open", default=list())
    hrsoperation = colander.SchemaNode(colander.String(), title="Hours of Operation", description="Your requested hours of operation!", missing=unicode(''), widget=deform.widget.TextAreaWidget(rows=10, cols=60))
    power = EventPowers(title="Power required", default=list())
    tables = colander.SchemaNode(colander.Int(), title="Tables", default=0)
    chairs = colander.SchemaNode(colander.Int(), title="Chairs", default=0)
    wiredaccess = EventDrops(title="Wired access", description="If you need wired access to the DEF CON network let us know.", default=list())
    wirelessap = EventAPS(title="Wireless AP", description="If you require your own wireless access point (we don't provide hardware), we need the details to give on to the DEF CON NOC", default=list())
    represent = colander.SchemaNode(colander.String(), title="Representation", description="Who will be representing this contest/event on stage. Black badge events will be at DEF CON closing ceremonies, non-black badge events will be at CnE closing ceremonies. You will be notified if you are a black badge event or not.")
    numparticipants = colander.SchemaNode(colander.Int(), title="Number of Participants", description="This is a rough estimate of the expected number of participants.", default=0)
    otherrequests = TicketForm(title="Extra Requests:")

class EventBadge(colander.Schema):
    id = colander.SchemaNode(colander.Integer(), widget=deform.widget.HiddenWidget(), title="id", default=-1)
    typeof = colander.SchemaNode(colander.Int(), title="Badge Type", default=0, widget=deform.widget.SelectWidget(values=[(key, value) for (key, value) in badge_types.items()]), description="Badge type")
    amount = colander.SchemaNode(colander.Int(), title="Amount", default=0, description="The amount of badges of this type that should be made available")
    why = colander.SchemaNode(colander.String(), missing=u'', description="Add a reason for the amount requested, for our records.")

class EventBadges(colander.SequenceSchema):
    badge = EventBadge(title="Badges")

class EventManagement(CSRFSchema):
    status = colander.SchemaNode(colander.Int(), title="Status", default='0', widget=deform.widget.SelectWidget(values=[(key, value) for (key, value) in status_types.items()]), description="Change status of contest/event")
    badges = EventBadges(description="Add types of badges and amount for this contest/event")
    blackbadge = colander.SchemaNode(colander.Bool(), title="Black Badge", default=False, description="Whether this event is a black badge event or not")
    email = colander.SchemaNode(colander.Bool(), title="Send Email", default=False, description="Send an email notifying contest owners of change?")

