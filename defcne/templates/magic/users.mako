<%inherit file="../site.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <%include file="sidebar.mako" />
        <div id="Content" class="span9">
            <h3>${page_title if page_title else ''}</h3>
            % if users:
            <table class="table table-striped table-condensed table-bordered">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Groups</th>
                        <th>Validated</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    % for user in users:
                    <tr>
                        <td><a href="${user['view_url']}">${user['username']}</a></td>
                        <td>${user['email']}</td>
                        <td>
                            % for group in user['groups']:
                            ${group} 
                            % endfor
                        </td>
                        <td> 
                            % if user['validated']:
                            <i class="icon-ok"></i>
                            % else:
                            <i class="icon-remove"></i>
                            % endif
                        </td>
                        <td>
                            <a href="${user['edit_url']}" class="btn btn-small btn-danger">Edit User</a>
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

