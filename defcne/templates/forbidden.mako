<%inherit file="site.mako" />

<div class="jumbotron">
    <h1>Uh oh ... 403</h1>
    <h3>Access Forbidden</h3>
    <p class="lead">
        You do not have the required permission to access the page requested.
    </p>
</div>

<%block name="title">${parent.title()} - Uh oh ... access is forbidden!</%block>

