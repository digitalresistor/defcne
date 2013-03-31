<%inherit file="site.mako" />

<div class="jumbotron">
    <h1>Uh oh ... 400</h1>
    <h3>Bad Request</h3>
    <p class="lead">
        You unfortunately sent a request we couldn't process. Please try again!
    </p>
</div>

<%block name="title">${parent.title()} - Uh oh ... bad request!</%block>

