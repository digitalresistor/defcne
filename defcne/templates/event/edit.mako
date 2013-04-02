<%inherit file="../deform.mako" />

<div class="container-fluid">
    <div class="row-fluid">
        <div id="Content" class="span9">
            <h3>${page_title if page_title else ''}</h3>
% if form:
    ${form|n}
% endif
        </div>
    </div>
</div>

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>

