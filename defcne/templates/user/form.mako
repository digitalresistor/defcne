<%inherit file="../deform.mako" />

<h1>${page_title if page_title else ''}</h1>

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span6">
        <p>
% if form:
    ${form|n}
% endif
        </p>
        </div>
        <div class="span6">
% if explanation:
<p>
    ${explanation|n}
</p>
% endif
        </div>
    </div>
</div>


<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>

