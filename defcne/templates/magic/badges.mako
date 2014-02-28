<%inherit file="../site.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <%include file="sidebar.mako" />
        <div id="Content" class="span9">
            <h3>${page_title if page_title else ''}</h3>
            % if events:
                <h4>Totals:</h4>
                <p>
                    <ul>
                        % for cnt in count:
                            <li><b>${cnt['name']}:</b> ${cnt['amount']}</b></li>
                        % endfor
                    </ul>
                </p>
            <table class="table table-striped table-condensed table-bordered">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Black Badge</th>
                        <th>Badges</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    % for event in events:
                    <tr>
                        <td><a href="${event['magic_url']}">${event['name']}</a></td>
                        <td>${event['status']}</td>
                        <td>
                            % if event['blackbadge']:
                            <i class="icon-ok"></i>
                            % else:
                            <i class="icon-remove"></i>
                            % endif
                        </td>
                        <td>
                            <ul>
                            % for badge in event['badges']:
                                <li><b>${badge['typeof']}:</b> ${badge['amount']}</li>
                            % endfor
                            </ul>
                        <td>
                            <a href="${event['edit_url']}" class="btn btn-small btn-primary">Edit</a>
                            <a href="${event['manage_url']}" class="btn btn-small btn-danger">Manage Event</a>
                        </td>
                    </tr>
                    % endfor
                </tbody>
            </table>
            %endif
        </div>
    </div>
</div>

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>
<%block name="flash"><%include file="../flash.mako" args="queue_name='magic', alert_type='success'" /></%block>

