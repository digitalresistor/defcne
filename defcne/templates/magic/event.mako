<%inherit file="../site.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <%include file="sidebar.mako" />
        <div id="Content" class="span9">
            <h3>${page_title if page_title else ''}</h3>
            <p><b>Description:</b></p>
            <p style="white-space: pre-wrap">${event['description']}</p>
            % if len(event['logo']) != 0:
            <p><b>logo</b>:</p> 
            <p><img src="${request.static_url(event['logo'])}" style="max-height: 200px; max-width: 200px;"></p>
            % endif
            <ul>
                <li><b>shortname</b>: ${event['shortname']}</li>

                % if len(event['hrsofoperation']) != 0:
                <li><b>Hours of Operation</b>:
                <p style="white-space: pre-wrap">${event['hrsofoperation']}</p>
                </li>
                % endif
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

                % if len(event['power']) != 0:
                <li><b>Power Requirements</b>:
                <div>
                    % for power in event['power']:
                    <ul>
                        <li><b>Amps</b>: ${power['amps']}</li>
                        <li><b>Outlets</b>: ${power['outlets']}</li>
                        <li><b>Justification</b>: ${power['justification']}</li>
                    </ul>
                    % endfor
                </div>
                </li>
                % endif

                % if len(event['drops']) != 0:
                <li><b>Network Drops</b>:
                <div>
                    % for drop in event['drops']:
                    <ul>
                        <li><b>Type</b>: ${drop['typeof']}</li>
                        <li><b>Justification</b>: ${drop['justification']}</li>
                    </ul>
                    % endfor
                </div>
                </li>
                % endif

                % if len(event['aps']) != 0:
                <li><b>Wireless Accesspoints</b>:
                <div>
                    % for ap in event['aps']:
                    <ul>
                        <li><b>Hardware MAC</b>: ${ap['hwmac']}</li>
                        <li><b>AP Brand</b>: ${ap['apbrand']}</li>
                        <li><b>SSID</b>: ${ap['ssid']}</li>
                    </ul>
                    % endfor
                </div>
                </li>
                % endif

                <li><b>Extra information/requests</b>: ${event['ticket_count']}</li>
            </ul>
            
            <p><a href="${event['edit_url']}" class="btn btn-primary">Edit Event</a> <a href="${event['manage_url']}" class="btn btn-danger">Manage Event</a></p>

            % if len(event['tickets']) == 0:
            <p>No additional information for this contest/event. Send request to contest owner below.</p>
            % else:
            % for ticket in event['tickets']:
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
<%block name="flash"><%include file="../flash.mako" args="queue_name='event', alert_type='success'" /></%block>

