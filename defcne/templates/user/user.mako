<%inherit file="../site.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <%include file="sidebar.mako" />
        <div id="Content" class="span9">
            <h3>Welcome ${request.user.user.disp_uname}</h3>
            <p></p>
            <h3>Contests/Events/Villages</h3>
            % if not events or not len(events):
            <p>You have no events or contests. You should go <a href="${request.route_url('defcne.e', traverse=('create'))}">create one</a>!</p>
            % else:
                <%include file="events.mako" args="events=events" />
            % endif
        </div>
    </div>
</div>

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>
<%block name="flash"><%include file="../flash.mako" args="queue_name='user', alert_type='success'" /></%block>

