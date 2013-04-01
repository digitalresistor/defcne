# File: Event.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-03-03

import colander
import deform

from pyramid_deform import SessionFileUploadTempStore
from urlparse import urlparse

from csrf import CSRFSchema

from .. import models as m

"""
Questions:

    1. Contest name
    2. Contest description (markdown?)
    3. Contest website
    4. Contest logo (upload file)
    5. Contest POC (Add additional staff members here)
        1. Name/Email Address/Cell phone
    6. Contest POC cell phone
    7. Days and hours of operation (open ended)
    8. Do you need power?
    9. Tables you are requesting
    11. How many chairs?
    12. Wired access to DefCon network
        1. How many drops
        2. Copper or Fiber (Fiber may not be available)
        3. Justify why you need it
    13. Are you planning on having a wireless AP?
        1. Hardware address/AP brand/SSID
    14. Who will be representing your contest or event at closing?
    15. Please provide a rudimentary schedule of your primary in room contact
    16. Will you use the stage and microphone in the contest area to make announcements?
    18. Expected number of participants
    19. General requests ... (trash cans, small farm animals, lube ... you know, anything else.)

"""

@colander.deferred
def upload_widget(node, kw):
    request = kw['request']
    tmpstore = SessionFileUploadTempStore(request)
    return deform.widget.FileUploadWidget(tmpstore)

class EventPOC(colander.Schema):
    """Form that gets event point of contacts"""
    name = colander.SchemaNode(colander.String(), title="Name")
    email = colander.SchemaNode(colander.String(), title="Email address")
    cellphone = colander.SchemaNode(colander.String(), title="Cell phone", missing=unicode(''))

class EventPOCS(colander.SequenceSchema):
    poc = EventPOC(title="Staff")

class EventPower(colander.Schema):
    amps = colander.SchemaNode(colander.Int(), title="Amps required")
    outlets = colander.SchemaNode(colander.Int(), title="Outlets required")
    justify = colander.SchemaNode(colander.String(), title="Justification", description="Please justify your requirement.")

class EventPowers(colander.SequenceSchema):
    power = EventPower()

class EventDrop(colander.Schema):
    typeof = colander.SchemaNode(colander.String(), title="Preferred", default='copper', widget=deform.widget.SelectWidget(values=(('copper', 'Copper'), ('fiber', 'Fiber'))), description="Choice may not be available. We will do our best!")
    justify = colander.SchemaNode(colander.String(), title="Justification", description="Please justify your requirement.")

class EventDrops(colander.SequenceSchema):
    drop = EventDrop()

class EventAP(colander.Schema):
    hwmac = colander.SchemaNode(colander.String(), title="Wireless MAC address")
    apbrand = colander.SchemaNode(colander.String(), title="Brand Name")
    ssid = colander.SchemaNode(colander.String(), title="SSID")

class EventAPS(colander.SequenceSchema):
    ap = EventAP()


def event_verify_name_not_used(node, value):
    if m.Event.find_event(value) != None:
        raise colander.Invalid(node, msg='Event name already exists. Please choose another name.')

def event_verify_shortname_not_used(node, value):
    if ' ' in value:
        raise colander.Invalid(node, msg='Short name should not contain any spaces.')

    if m.Event.find_event_short(value) != None:
        raise colander.Invalid(node, msg='Short name already exists. Please choose another name.')

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
    name = colander.SchemaNode(colander.String(), title="Contest/Event Name", validator=event_verify_name_not_used)
    shortname = colander.SchemaNode(colander.String(), title="Short Name", description="A short name that doesn't include spaces", validator=event_verify_shortname_not_used)
    description = colander.SchemaNode(colander.String(), title="Description", widget=deform.widget.TextAreaWidget(rows=5, cols=60))
    website = colander.SchemaNode(colander.String(), title="Website URL", missing=unicode(''), validator=event_verify_website_name)
    logo  = colander.SchemaNode(deform.FileData(), widget = upload_widget, missing=None)
    pocs = EventPOCS(title="Event Staff", description="Other points of contact if you are not available, along with people that would be allowed access to contest/events before open", default=list())
    hrsoperation = colander.SchemaNode(colander.String(), title="Hours of Operation", description="Your requested hours of operation!", missing=unicode(''), widget=deform.widget.TextAreaWidget(rows=10, cols=60))
    power = EventPowers(title="Power required", default=list())
    tables = colander.SchemaNode(colander.Int(), title="Tables", default=0)
    chairs = colander.SchemaNode(colander.Int(), title="Chairs", default=0)
    wiredaccess = EventDrops(title="Wired access", description="If you need wired access to the DEFCON network let us know.", default=list())
    wirelessap = EventAPS(title="Wireless AP", description="If you require your own wireless access point (we don't provide hardware), we need the details to give on to the DEFCON NOC", default=list())
    represent = colander.SchemaNode(colander.String(), title="Representation", description="Who will be representing this contest/event on stage. Black badge events will be at DEFCON closing ceremonies, non-black badge events will be at CnE closing ceremonies. You will be notified if you are a black badge event or not.")
    numparticipants = colander.SchemaNode(colander.Int(), title="Number of Participants", description="This is a rough estimate of the expected number of participants.", default=0)

