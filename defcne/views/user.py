# File: user.py
# Author: Bert JW Regeer <bertjw@regeer.org>
# Created: 2013-01-20

from ..forms import UserForm

from deform import Form

def create(request):
    schema = UserForm()
    uf = Form(schema, action=request.route_url('defcne.user.create'), buttons=('submit',))
    return {'form': uf.render()}
