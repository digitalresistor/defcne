<!DOCTYPE html>
<html lang="en">
    <head><%block name="head">
        <title><%block name="title"></%block></title>
        <link rel="shortcut icon" href="${request.static_url('defcne:static/favicon.ico')}">
        <%block name="stylesheets">
        <link rel="stylesheet" href="${request.static_url('defcne:static/defcne.css')}" type="text/css" media="screen" />
        </%block>
        <meta charset="utf-8" />
        <%block name="javascript"></%block>
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

        <%block name="end"></%block>
    </body>
</html>

