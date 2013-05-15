<%inherit file="../site.mako" />

<h1><a href="${event['url']}">${page_title if page_title else ''}</a></h1>
<div class="container-fluid">
    <div class="row-fluid">
        <div class="span12">
            <p style="white-space: pre-wrap;">${event['description']}</p>
            % if len(event['website']) != 0:
            <p class="eventwebsite">You may be able to find more information on the contest/event website: <a href="${event['website']}">${event['website']}</a></p>
            % endif
            <div class="share">
                <a href="https://twitter.com/share" class="twitter-share-button" data-text="Check out this contest/event at #DEFCON: ${event['name']}">Tweet</a>
                <div class="g-plusone" data-size="medium"></div>
                <div class="fb-like" data-send="false" data-layout="button_count" data-width="450" data-show-faces="true"></div>
             </div>
         </div>
     </div>
 </div>

<%block name="title">${parent.title()} ${' - ' + page_title if page_title else ''}</%block>
<%block name="javascript_end">
    ${parent.javascript_end()}
    <script type="text/javascript">
        !function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');
    </script>
    <script type="text/javascript">
        (function() {
             var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
             po.src = 'https://apis.google.com/js/plusone.js';
             var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
         })();
     </script>

    <div id="fb-root"></div>
    <script type="text/javascript">
        (function(d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) return;
            js = d.createElement(s); js.id = id;
            js.src = "//connect.facebook.net/en_US/all.js#xfbml=1";
            fjs.parentNode.insertBefore(js, fjs);
        }(document, 'script', 'facebook-jssdk'));</script>
</%block>
