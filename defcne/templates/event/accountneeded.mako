<%inherit file="../site.mako" />

<%block name="maincontent">

<h1>Create a new Contest or Event</h1>

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span12">
            <h3>Not so fast ...</h3>
            <p>Before continuing on, we require that you create a new user account that will be associated with your event. This allows us to be in constant communication with you regarding your contest or event and help you make it a huge success.</p>
        </div>
    </div>
    <div class="row-fluid">
        <div class="span12" style="text-align: center;">
            <h3>Do you have what it takes to run a contest or event?</h3>
        </div>
    <div class="row-fluid">
        <div class="span4" style="text-align: center;">
            <a href="${request.route_url('defcne.user', traverse='create')}" class="btn btn-danger">Create an Account</a>
        </div>
        <div class="span4" style="text-align: center;">
            <a href="${request.route_url('defcne.user', traverse='auth', _query=(('next', request.path),))}" class="btn btn-primary">Authenticate and Go!</a>
        </div>
        <div class="span4" style="text-align: center;">
            <a href="${request.route_url('defcne')}" class="btn">Nevermind. Not interested!</a>
        </div>
    </div>
</div>

</%block>


<%block name="title">${parent.title()} - Create new Contest or Event</%block>
