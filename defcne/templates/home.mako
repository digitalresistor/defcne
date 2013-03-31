<%inherit file="site.mako" />

<div class="jumbotron">
    <h1>DEFCON</h1>
    <h1>Contests and Events</h1>
    <p class="lead">
        This years contests and events at DEFCON are going to be absolutely fantastic!
    </p>
</div>
<hr>
<div class="container-fluid">
    <div class="row-fluid">
        <div class="span4">
            <h3><a href="${request.route_url('defcne.e', traverse='')}">Events</a></h3>
            <p>Learn about the events that are going to be at DEFCON</p>
            &gt;&gt; <a href="${request.route_url('defcne.e', traverse='')}">See all events</a>
        </div>
        <div class="span4">
            <h3><a href="#">Goons</a></h3>
            <p>Learn more about the red badge wearing badasses that help make your conference experience awesome</p>
            &gt;&gt; <a href="#">Learn more about the goons</a>
        </div>
        <div class="span4">
            <h3>Participate</h3>
            &gt;&gt; <a href="${request.route_url('defcne.e', traverse='create')}">Create an event</a><br>
            &gt;&gt; <a href="#">More info</a><br>
            &gt;&gt; <a href="#">F.A.Q</a>
        </div>
    </div>
</div>

<%block name="title">${parent.title()} - Home</%block>
