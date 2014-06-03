import colander
import deform

from .. import models as m
from ..models.cvebase import (
        badge_types,
        status_types,
        )

from csrf import CSRFSchema
from schemaform import SchemaFormMixin

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
    #blackbadge = colander.SchemaNode(colander.Bool(), title="Black Badge", default=False, description="Whether this event is a black badge event or not")
    #email = colander.SchemaNode(colander.Bool(), title="Send Email", default=False, description="Send an email notifying contest owners of change?")

class ContestManagement(CSRFSchema):
    status = colander.SchemaNode(colander.Int(), title="Status", default='0', widget=deform.widget.SelectWidget(values=[(key, value) for (key, value) in status_types.items()]), description="Change status of contest/event")
    badges = EventBadges(description="Add types of badges and amount for this contest/event")
    blackbadge = colander.SchemaNode(colander.Bool(), title="Black Badge", default=False, description="Whether this event is a black badge event or not")
    #email = colander.SchemaNode(colander.Bool(), title="Send Email", default=False, description="Send an email notifying contest owners of change?")

class VillageManagement(CSRFSchema):
    status = colander.SchemaNode(colander.Int(), title="Status", default='0', widget=deform.widget.SelectWidget(values=[(key, value) for (key, value) in status_types.items()]), description="Change status of contest/event")
    badges = EventBadges(description="Add types of badges and amount for this contest/event")
    #email = colander.SchemaNode(colander.Bool(), title="Send Email", default=False, description="Send an email notifying contest owners of change?")
