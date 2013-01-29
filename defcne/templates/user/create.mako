<%inherit file="../site.mako" />

This is the create page ...

${form|n}

<%block name="javascript">
    ${parent.javascript()}
    <script type="text/javascript" src="${request.static_url('deform_bootstrap:static/bootstrap.min.js')}"></script>
    <script type="text/javascript" src="${request.static_url('deform:static/scripts/jquery-1.4.2.min.js')}"></script>
    <script type="text/javascript" src="${request.static_url('deform:static/scripts/deform.js')}"></script>
    <script type="text/javascript" src="${request.static_url('deform_bootstrap:static/deform_bootstrap.js')}"></script>
</%block>
<%block name="stylesheets">
    ${parent.stylesheets()}
    <link rel="stylesheet" href="${request.static_url('deform_bootstrap:static/deform_bootstrap.css')}" type="text/css" />
</%block>
<%block name="end">
    ${parent.end()}
    <script type="text/javascript">
        deform.load()
    </script>
</%block>

