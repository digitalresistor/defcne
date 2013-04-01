<%inherit file="../deform.mako" />

<h1>${page_title if page_title else ''}</h1>

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span8">
        <p>
% if form:
    ${form|n}
% endif
        </p>
        </div>
        <div class="span4">
% if explanation:
<p>
    ${explanation|n}
</p>
% endif
        </div>
    </div>
</div>


<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>

