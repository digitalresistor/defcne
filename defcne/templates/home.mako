<%inherit file="site.mako" />

This is the new homepage ...

% if user:
    ${user}
% endif

<p>

% if not user:
<a href="/user/auth/">Authenticate</a> <br />
% else:
<a href="/user/deauth/">Deauthenticate</a> <br />
% endif
<a href="/user/create/">Create</a> <br />
<a href="/user/validate/">Validate</a> <br />
</p>
