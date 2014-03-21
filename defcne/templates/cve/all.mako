<%inherit file="../site.mako" />

% if len(events) is 0:
<div class="jumbotron">
    <h1>${page_title if page_title else ''}</h1>
    <h2>Sadly, there are no ${type} yet!</h2>
    <p class="lead">
    The ${type} at ${page_title if page_title else ''} are going to be absolutely fantastic, so check back often.
    </p>
</div>
% else:
<h1>${page_title if page_title else ''}</h1>
<div class="container-fluid">
    <div class="row-fluid">
        <div class="span12">
            <p>DEF CON ${request.context.dc} has a lot of exciting ${type} that are going to make your DEF CON experience even better.</p>
            <p>Take a look at what is going to be on offer this year, and find something that excites you!</p>

            % for event in events:
            <div class="event">
                <div class="name"><a href="${event['url']}">${event['name']}</a></div>
                <div class="description">${event['description']}</div>
                <div class="extrastuff"><ul><li><a href="${event['website']}">${event['website']}</a></li><li><a href="${event['url']}">More</a></li></ul></div>
            </div>
            % endfor
        </div>
    </div>
</div>
% endif

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>


