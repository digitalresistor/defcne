<%page args="queue_name='', alert_type='success'"/>

<%
messages = request.session.pop_flash(queue=queue_name)
if not len(messages):
    return
%>

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span12 alert ${'alert-' + alert_type if alert_type else ''}">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            % for message in messages:
            <div>
                ${message}
            </div>
            % endfor
        </div>
    </div>
</div>

