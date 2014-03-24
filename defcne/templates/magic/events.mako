<%inherit file="../site.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <%include file="sidebar.mako" />
        <div id="Content" class="span9">
            <h3>${page_title if page_title else ''}</h3>
            % if cves:
            <table class="table table-striped table-condensed table-bordered">
                <thead>
                    <tr>
                    % for (_, th, _) in listitems:
                        <th>${th}</th>
                    % endfor
                    </tr>
                </thead>
                <tbody>
                % for cve in cves:
                <tr>
                    % for (it, _, type) in listitems:
                    <td>
                        % if type == 'text':
                            ${cve[it]}
                        % elif type == 'boolean':
                            % if cve[it]:
                                Yes
                            % else:
                                No
                            % endif
                        % elif type == 'url':
                            <a href="${cve[it][1]}">${cve[it][0]}</a>
                        % elif type == 'list':
                            % if len(cve[it[1]]) > 0:
                                % for li in cve[it[1]]:
                                <br />
                                <ul>
                                % for (iit, ift, itype) in it[0]:
                                    <li><b>${ift}</b>: ${li[iit]}</li>
                                % endfor
                                </ul>
                                % endfor
                            % else:
                                None
                            % endif
                        % elif type == 'buttons':
                            % for button in cve[it]:
                                <a href="${button[1]}" class="btn btn-small btn-primary">${button[0]}</a>
                            % endfor
                        % endif
                    </td>
                    % endfor
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

