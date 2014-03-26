<%inherit file="../deform.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <%include file="sidebar.mako" />
        <div id="Content" class="span9">
            <h3>${page_title if page_title else ''}</h3>
            % if len(cve['tickets']) == 0:
            <p>No additional information for this contest/cve. Feel free to send us a request below!</p>
            % else:
            % for ticket in cve['tickets']:
            <div class="extrainfo"><p style="white-space: pre-wrap">${ticket.ticket}</p><div class="userdate" style="text-align: right;">${ticket.user.disp_uname}<br />${ticket.created.isoformat()}</div></div>
            % endfor
            <p>Feel free to respond or add more information using the form below.</p>
            % endif
            <hr />
            % if form:
            <h4>Add more information:</h4>
            ${form|n}
            % endif
        </div>
    </div>
</div>

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>
<%block name="flash"><%include file="../flash.mako" args="queue_name='cve_info', alert_type='success'" /></%block>


