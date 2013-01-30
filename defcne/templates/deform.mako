<%inherit file="site.mako" />

% if hasattr(next, "body"):
    ${next.body()}
% endif

<%block name="stylesheets">
    ${parent.stylesheets()}
    ##<link rel="stylesheet" href="${request.static_url('deform_bootstrap:static/deform_bootstrap.css')}" type="text/css" />
</%block>

<%block name="javascript_end">
    ${parent.javascript_end()}
    <script type="text/javascript" src="${request.static_url('deform:static/scripts/deform.js')}"></script>
    <script type="text/javascript" src="${request.static_url('deform_bootstrap:static/deform_bootstrap.js')}"></script>
    <script type="text/javascript">
        deform.load()
    </script>
</%block>

