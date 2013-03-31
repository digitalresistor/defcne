<%inherit file="site.mako" />

<div class="jumbotron">
    <h1>Uh oh ... 404</h1>
    <h3>Not Found</h3>
    <p class="lead">
        The page you are looking for doesn't exist!
    </p>
</div>

<%block name="title">${parent.title()} - Uh oh ... page was not found!</%block>
