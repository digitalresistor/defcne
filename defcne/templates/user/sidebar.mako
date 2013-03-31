<aside class="span3">
    <nav class="well sidebar-nav">
        <ul class="nav nav-list">
            <li><a href="${request.route_url('defcne.user', traverse='')}">User Home</a></li>
            <li><a href="${request.route_url('defcne.user', traverse=('profile'))}">My Profile</a></li>
            <li><a href="${request.route_url('defcne.user', traverse=('edit', 'password'))}">Change Password</a></li>
        </ul>
    </nav>
</aside>
