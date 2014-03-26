import colander
import deform

from pyramid_deform import SessionFileUploadTempStore
from urlparse import urlparse

from csrf import CSRFSchema

from .. import models as m
from Ticket import TicketForm
from schemaform import SchemaFormMixin

@colander.deferred
def upload_widget(node, kw):
    request = kw['request']
    tmpstore = SessionFileUploadTempStore(request)
    return deform.widget.FileUploadWidget(tmpstore)

class POC(colander.Schema):
    """Form that gets event point of contacts"""
    id = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget(), title="id", default=-1)
    name = colander.SchemaNode(colander.String(), title="Name")
    email = colander.SchemaNode(colander.String(), title="Email address")
    cellphone = colander.SchemaNode(colander.String(), title="Cell phone", missing=unicode(''))

class POCS(colander.SequenceSchema):
    poc = POC(title="Staff")

class Power(colander.Schema):
    id = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget(), title="id", default=-1)
    outlets = colander.SchemaNode(colander.Int(), title="Outlets required")
    justification = colander.SchemaNode(colander.String(), title="Justification", description="Please justify your requirement.")
    threephase = colander.SchemaNode(colander.Boolean(), title="3 Phase power", description="Do you require 3-phase power?") 

class Powers(colander.SequenceSchema):
    power = Power()

class WiredInternet(colander.Schema):
    id = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget(), title="id", default=-1)
    justification = colander.SchemaNode(colander.String(), title="Justification", description="Please justify your requirement.")

class WiredInternets(colander.SequenceSchema):
    drop = WiredInternet()

class AccessPoint(colander.Schema):
    id = colander.SchemaNode(colander.String(), widget=deform.widget.HiddenWidget(), title="id", default=-1)
    hwmac = colander.SchemaNode(colander.String(), title="Wireless MAC address")
    apbrand = colander.SchemaNode(colander.String(), title="Brand Name")
    ssid = colander.SchemaNode(colander.String(), title="SSID")

class AccessPoints(colander.SequenceSchema):
    ap = AccessPoint()

@colander.deferred
def deferred_event_verify_name_not_used(node, kw):
    type = kw['type']

    def event_verify_name_not_used(node, value):
        if 'origname' in kw:
            if kw.get('origname') == value.lower():
                return

        if m.CVEBase.find(type, value) != None:
            raise colander.Invalid(node, msg='Name already exists, please choose a different name.')

    return event_verify_name_not_used

@colander.deferred
def deferred_name_title(node, kw):
    return '{} Name'.format(kw['type'].capitalize())

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

class CVEBase(CSRFSchema, SchemaFormMixin):
    __buttons__ = (deform.form.Button(name="Submit",),)
    
    id = colander.SchemaNode(colander.Integer(), widget=deform.widget.HiddenWidget(), title="id", missing=None)
    name = colander.SchemaNode(colander.String(), validator=deferred_event_verify_name_not_used, title=deferred_name_title)
    oneliner = colander.SchemaNode(colander.String(), title="Summary", description="One line description")
    description = colander.SchemaNode(colander.String(), title="Description", widget=deform.widget.TextAreaWidget(rows=5, cols=60))
    website = colander.SchemaNode(colander.String(), title="Website URL", missing=unicode(''), validator=event_verify_website_name)
    logo = colander.SchemaNode(deform.FileData(), widget=upload_widget, missing=None)
    pocs = POCS(title="Staff", description="People that are part of the team helping make this a success.", default=list())


