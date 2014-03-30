<%inherit file="site.mako" />

<h1>Frequently asked Questions and Guidelines</h1>


<div class="container-fluid">
    <div class="row-fluid">
        <div class="span12">
            <h3>Tips, Guidelines, and Gotcha's</h3>

            <ol>
                <li>This year, there are additional resources to help your
                contests &amp; events with the cost of expanding/becoming
                bigger and better. So if you have an earth shattering idea but
                you’re tight on cash, submit your idea and tell us how we can
                help.</li>

                <li><strong>This year, no contest has been pre-approved for a
                black badge!</strong> Please do not advertise that you're
                getting one until we have given you the confirmation. DETAILS
                coming soon on the criteria for black badge.  Please follow in
                DEF CON forums for updates on this topic.</li>

                <li>The pre-con meeting is Wednesday morning for the Contests,
                Events, and Villages (CEV) Points Of Contact (POCs). You need
                at least one person to attend; if you absolutely can't attend,
                you will need to let the CEV head (Pyr0) know well in advance.
                This meeting is where we will discuss any last minute changes,
                introduce you to the goon staff, set ground rules, and address
                any issues you might have. If you fail to attend this meeting
                or you don't let Pyr0 know that you’ll be absent, your contest
                or event will be cancelled and your space awarded to one of the
                many people who’ll be happy to take your place.</li>

                <li>Please fill out the entire form. If there are additional
                requests, favors owed, comments or other important commitments,
                please let us know when you submit this form. Please be
                thorough, and complete.</li>

                <li>Please make provisions to bring your own prizes to give
                away. Hit up various vendors and tell them that it's for DEF
                CON, you might be surprised by how giving they are. It's best
                to come prepared so no one is disappointed.</li>

                <li>This year all "official contests" will qualify for contest
                badges, and approved "unofficial contests" will receive two
                human badges. If you are a large official contests/event you
                may need to request additional badges for your support staff.
                Once your contest/event has been selected for DEF CON 22, your
                badge requests will be reviewed by the CEV Goon Staff.  Our
                recommendations will be turned over to Will, DEF CON Chief of
                Staff for final approval. All volunteers are expected to work
                no LESS than 8 hours per day (every day) to earn a badge. If
                you abuse this (as many have in the past) you will not be asked
                to return.</li>

                <li>The Contest Description, Name, and POC name will all be
                included in the DEF CON 22 program, so please ensure it's
                written how you want it to read. If you don't give us your
                information, you’ll not be included in the program: and that
                would just be sad.</li>

                <li>Please provide links to any webpages, Facebook page,
                Twitter names, Flicker feeds, etc. We plan to promote contests
                on the DEF CON Facebook page and Twitter feed. If you’ll be
                tweeting updates, please let us know. We’ll  create a Twitter
                list so attendees can easily follow all the action, and provide
                constant Facebook updates. Be sure to get on that list!
                Consider following @TCMBC on twitter for forum and other DEF
                CON service updates. If a forum is missing for your approved
                contest/event, or has a bad description, please let him
                know!</li>

                <li>Booth Creativity: It is natural, and expected, that you
                will dress up the space where your contest or event will be
                held.  Here are some pointers: a) Never hang anything on the
                walls, only the hotel can do that. b) Be sure to bring magnets,
                the airwalls have a ferrous core and the hotel will love you
                for being prepared!</li>

                <li>You are NOT allowed to sell ANYTHING at your tables,
                Period. If you want to sell something, you need to contact the
                Vendor Dept. Head, Wiseacre for information on the Vendor Area,
                or speak with an already approved Vendor to share space. If
                you’re a non-profit (HACKER SPACES PAY ATTENTION!) and you
                would like to discuss fund raising options please contact Pyr0
                directly.</li>

                <li>You’ll be asked to provide continuous updates about your
                contest to the Info Booth, failure to do so will be marked
                against you next year</li>

                <li>As a reminder, you’ll need to find the Sr. Contest Goon and
                provide a final score and update for your contest no later than
                11:00AM on Sunday.   It must be submitted, either written or
                typed on a 8.5 in x 11 in sheet of paper. These final scores
                and updates will  be   posted  on the DEF CON website at the
                end of the conference, so please ensure it’s written the way
                you want it to read.</li>

                <li>In order to accommodate  early access to the contest area,
                we’ll need the REAL names of your volunteers, along with a
                clear digital picture (roughly 100x100dpi)  to give to RIO
                hotel security. They’ll be checking ID's and if your name isn't
                on the list you won't be   allowed access to the contest
                area.</li>

                <li>"Official contests" are contests that have been vetted and
                approved. If this is your first year and you’re approved,
                expect to be an "unofficial contest or event".</li>

                <li>There are two separate closing ceremonies, the Awards
                Ceremony for Contests, Events, and Villages and second the main
                closing ceremony. Your whole group is expected to attend
                both!</li>
            </ol>

        </div>
    </div>
    <div class="row-fluid">
        <div class="span12" style="text-align: center;">
            <h3>Do you have what it takes to run a contest or event?</h3>
        </div>
        <div class="row-fluid">
            <div class="span3" style="text-align: center;">
                <a href="${request.route_url('defcne.c', traverse='create')}" class="btn btn-primary">Submit Contest Proposal</a>
            </div>
            <div class="span3" style="text-align: center;">
                <a href="${request.route_url('defcne.e', traverse='create')}" class="btn btn-primary">Submit Event Proposal</a>
            </div>
            <div class="span3" style="text-align: center;">
                <a href="${request.route_url('defcne.v', traverse='create')}" class="btn btn-primary">Submit Village Proposal</a>
            </div>
            <div class="span3" style="text-align: center;">
                <a href="${request.route_url('defcne')}" class="btn">No longer interested!</a>
            </div>
        </div>
    </div>
</div>

<%block name="title">${parent.title()} - Create Contest or Event</%block>

