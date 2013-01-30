<!DOCTYPE html>
<html lang="en">
    <head><%block name="head">
        <title><%block name="title"></%block></title>
        <link rel="shortcut icon" href="${request.static_url('defcne:static/favicon.ico')}">
        <%block name="stylesheets">
            <link rel="stylesheet" href="${request.static_url('defcne:static/defcne.css')}" type="text/css" />
            <link rel="stylesheet" href="${request.static_url('defcne:static/bootstrap/css/bootstrap.min.css')}" type="text/css" />
        </%block>
        <meta charset="utf-8" />
        <%block name="javascript_head"></%block>
    </%block></head>
    <body>
        <header>
        <%block name="header"></%block>
        </header>
        <div id="Main">
            % if hasattr(next, "body"):
                ${next.body()}
            % endif
        </div>
        <aside>
        <nav>
        <%block name="menu"></%block>
        </nav>
        </aside>

        <footer>
        <%block name="footer"></%block>
        </footer>
    </body>
    <%block name="javascript_end">
        <script type="text/javascript" src="${request.static_url('defcne:static/jquery-1.9.0.min.js')}"></script>
        <script type="text/javascript" src="${request.static_url('defcne:static/bootstrap/js/bootstrap.min.js')}"></script>
    </%block>
</html>

