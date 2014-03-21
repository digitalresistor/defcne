<%inherit file="site.mako" />

<div class="jumbotron">
    <h1>DEF CON</h1>
    <h2>Contests Events Villages</h2>
    <p class="lead">
        This years contests, events and villages at DEF CON are going to be absolutely fantastic!
    </p>
</div>
<hr>
<div class="container-fluid">
    <div class="row-fluid">
        <div class="span6">
            <h3><a href="${request.route_url('defcne.e', traverse='')}">Events</a></h3>
            <p>Learn about the events that are going to be at DEF CON</p>
            &gt;&gt; <a href="${request.route_url('defcne.e', traverse='')}">See all events</a>
        </div>
        <div class="span6">
            <h3>Participate</h3>
            <ul>
                <li><a href="${request.route_url('defcne', 'guidelines')}">FAQ/Guidelines for Contests/Events/Villages</a></li>
                <li><a href="${request.route_url('defcne.c', traverse='create')}">Submit Contest proposal</a></li>
                <li><a href="${request.route_url('defcne.e', traverse='create')}">Submit Event proposal</a></li>
            </ul>
        </div>
    </div>
</div>

<%block name="title">${parent.title()} - Home</%block>
