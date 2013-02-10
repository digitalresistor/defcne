<!DOCTYPE html>
<html lang="en">
    <head><%block name="head">
        <title><%block name="title">DEFCON CnE</%block></title>
        <link rel="shortcut icon" href="${request.static_url('defcne:static/favicon.ico')}">
        <%block name="stylesheets">
            <link rel="stylesheet" href="${request.static_url('defcne:static/bootstrap/css/bootstrap.min.css')}" type="text/css" />
            <link rel="stylesheet" href="${request.static_url('defcne:static/defcne.css')}" type="text/css" />
        </%block>
        <meta charset="utf-8" />
        <%block name="javascript_head"></%block>
    </%block></head>
    <body class="container">
        <header class="masthead">
        <%block name="header">
        <h1><a href="${request.route_url('defcne')}">DEFCnE</a></h1>
        <p class="muted">Defcon Contests and Events</p>
        </%block>
        <%block name="navigation">
        <nav>
        <%block name="nav">
            <ul class="nav">
                <li><a href="${request.route_url('defcne')}">Home</a></li>
                <li><a href="${request.route_url('defcne')}">Events</a></li>
                <li><a href="${request.route_url('defcne')}">Goons</a></li>
                <li><a href="${request.route_url('defcne.user', traverse='auth')}">Authenticate</a></li>
            </ul>
        </%block>
        </nav>
        </%block>
        </header>

        <%block name="maincontent">
        <div id="Main" class="container">
            % if hasattr(next, "body"):
                ${next.body()}
            % endif
        </div>
        </%block>



        <footer>
        <%block name="footer"></%block>
        </footer>
    </body>
    <%block name="javascript_end">
        <script type="text/javascript" src="${request.static_url('defcne:static/jquery-1.9.1.min.js')}"></script>
        <script type="text/javascript" src="${request.static_url('defcne:static/bootstrap/js/bootstrap.min.js')}"></script>
    </%block>
</html>

