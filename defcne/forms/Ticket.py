# File: Ticket.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-04-09

import colander
import deform

from csrf import CSRFSchema

from .. import models as m

class TicketForm(CSRFSchema):
    """The ticket form ... """
    ticket = colander.SchemaNode(colander.String(), title="", widget=deform.widget.TextAreaWidget(rows=5, cols=60), missing=unicode(''))

