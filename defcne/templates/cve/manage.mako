<%inherit file="../site.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <%include file="sidebar.mako" />
        <div id="Content" class="span9">
            <h3>${page_title if page_title else ''}</h3>
            <p><b>Status:</b> ${cve['status']}</p>
            <p><b>Oneline:</b> ${cve['oneliner']}</p>
            <p><b>Description:</b></p>
            <p style="white-space: pre-wrap">${cve['description']}</p>
            % if len(cve['logo']) != 0:
            <p><b>logo</b>:</p>
            <p><img src="${request.static_url(cve['logo'])}" style="max-height: 200px; max-width: 200px;"></p>
            % endif
            <ul>
                % for (it, ft, type) in listitems:
                    <li>
                        % if len(ft) != 0:
                        <b>${ft}</b>:
                        % endif
                        
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
                        % endif
                    </li>
                % endfor
            </ul>
        </div>
    </div>
</div>

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>
<%block name="flash"><%include file="../flash.mako" args="queue_name='event', alert_type='success'" /></%block>


