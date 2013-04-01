<%inherit file="../site.mako" />

% if len(events) is 0:
<div class="jumbotron">
    <h1>${page_title if page_title else ''}</h1>
    <h2>Sadly, there are no contests or events yet!</h2>
    <p class="lead">
        The contests and events at ${page_title if page_title else ''} are going to be absolutely fantastic, so check back often.
    </p>
</div>
% else:
<h1>${page_title if page_title else ''}</h1>
<div class="container-fluid">
    <div class="row-fluid">
        <div class="span12">
            % for event in events:
                <div class="event">
                    <div class="name">${event['name']}</div>
                    <div class="description">${event['description']}</div>
                    <div class="website">${event['website']}</div>
                </div>
            % endfor
        </div>
    </div>
</div>
% endif

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>
