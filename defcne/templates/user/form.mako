<%inherit file="../deform.mako" />

<h1>${page_title if page_title else ''}</h1>

% if explanation:
<p>
    ${explanation}
</p>
% endif

% if form:
    ${form|n}
% endif

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>

