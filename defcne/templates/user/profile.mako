<%inherit file="../site.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <%include file="sidebar.mako" />
        <div id="Content" class="span9">
            <h3>Profile for ${request.user.user.disp_uname}</h3>
            <p>
                <ul class="profile">
                    % for field in profile_fields:
                    <li><b>${field[0]}</b>: 
                    % if isinstance(field[1], list):
                    <ul>
                        % for sfield in field[1]:
                            <li><b>${sfield[0]}</b>: ${sfield[1]}</li>
                        % endfor
                    </ul>
                    % else:
                    ${field[1]}
                    % endif
                    </li>
                    % endfor
                </ul>
            </p>
            <!-- <p><a href="${request.route_url('defcne.user', traverse=('edit', 'profile'))}">Edit Profile</a></p> -->
        </div>
    </div>
</div>


<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>
<%block name="flash"><%include file="../flash.mako" args="queue_name='user', alert_type='success'" /></%block>

