<%page args="events=None" />
<% if not len(events): return
num = 0
%>

<table class="table table-striped">
    <thead>
        <tr>
            <th>#</th>
            <th>Name</th>
            <th>Status</th>
            <th></th>
        </tr>
    </thead>
    <tbody>
        % for event in events:
        <% num += 1 %>
        <tr>
            <td>${num}</td>
            <td>${event['name']}</td>
            <td>${event['status']}</td>
            <td></td>
        </tr>
        % endfor
    </tbody> 
</table>
