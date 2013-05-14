<%inherit file="../site.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <%include file="sidebar.mako" />
        <div id="Content" class="span9">
            <h3>${page_title if page_title else ''}</h3>
            <p>You have no notices today.</p>
            <p><b>Description:</b></p>
            <p style="white-space: pre-wrap">${event['description']}</p>
            <ul>
                % if len(event['website']) != 0:
                <li><b>Website</b>: ${event['website']}</li>
                % endif
                <li><b>Tables</b>: ${event['tables']}</li>
                <li><b>Chairs</b>: ${event['chairs']}</li>
                % if len(event['pocs']) != 0:
                <li><b>Points of Contact</b>:
                <div>
                    <ul>
                        % for poc in event['pocs']:
                        <li>${poc}</li>
                        % endfor
                    </ul>
                </div>
                </li>
                % endif
            </ul>
        </div>
    </div>
</div>

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>
<%block name="flash"><%include file="../flash.mako" args="queue_name='event', alert_type='success'" /></%block>

