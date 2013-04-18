<!DOCTYPE html>
<html lang="en">
    <!--
    This is all Pyr0's fault.

    Don't believe me? That's probably for the best.

    Tech stack: FreeBSD, PostgreSQL, Python, Pyramid, SQLAlchemy, Deform, Bootstrap
    -->
    <head><%block name="head">
        <title><%block name="title">DEF CON CnE</%block></title>
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
        <p class="muted">DEF CON Contests and Events</p>
        </%block>
        <%block name="navigation">
        <nav>
        <%block name="nav">
            <ul class="nav">
                <li><a href="${request.route_url('defcne')}">Home</a></li>
                <li><a href="${request.route_url('defcne.e', traverse='')}">Events</a></li>
                <!-- <li><a href="${request.route_url('defcne')}">Goons</a></li> -->
                % if request.user.username is None:
                    <li><a href="${request.route_url('defcne.user', traverse='auth')}">Auth</a></li>
                % else:
                    <li><a href="${request.route_url('defcne.user', traverse='')}">Manage Account</a></li>
                    <li><a href="${request.route_url('defcne.user', traverse='deauth')}">Deauth</a></li>
                % endif
            </ul>
        </%block>
        </nav>
        </%block>
        </header>

        <%block name="maincontent">
        <div id="Main" class="container">
            <%block name="flash"></%block>
            % if hasattr(next, "body"):
                ${next.body()}
            % endif
        </div>
        </%block>

        <footer>
        <%block name="footer">
        <div>Copyright (c) 2013 - <a href="${request.route_url('defcne', traverse='')}">DEFCnE</a>. Created by <a href="http://bertjwregeer.com/">Bert JW Regeer</a>. Powered by <a href="http://www.pylonsproject.org">Pyramid</a>.</div>
        </%block>
        </footer>
    </body>
    <%block name="javascript_end">
        <script type="text/javascript" src="${request.static_url('defcne:static/jquery-1.9.1.min.js')}"></script>
        <script type="text/javascript" src="${request.static_url('defcne:static/bootstrap/js/bootstrap.min.js')}"></script>
    </%block>
</html>

