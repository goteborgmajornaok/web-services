# GMOK Web services

Welcome to GMOK web services, mainly a couple of integrations between Wordpress and Eventor as a REST-API implemented
with [Python/Flask](https://flask.palletsprojects.com/en/2.2.x/).

## Endpoints

Here follows a brief description of the endpoints implemented:

### /

Returns currently nothing.

### /members

Fetch member records, if validated member in organization (using Eventor). Returns an XLS-sheet of name, age and contact
information of each club member.

### /register

Register a Wordpress user, if validated member in organization (using Eventor).

### /calendarfeed

POST: fetch activities and events from Eventor & IdrottOnline, save to 'latest_calendar.ics' Requires API key (specified
in [config.cfg](config.cfg)) specified in header, and for how many days in advance that will be fetched.
GET: retrieve calendar feed previously saved to 'latest_calendar.ics'.

### /inventory

Set Wordpress member roles according to Eventor status. E.g., degrade from member to inactive if no longer in club,
or upgrade from guest member to member. Requires API key (specified in [config.cfg](config.cfg)) in header.

## Getting started

For running a local machine, conda is highly recommended. If you are new to conda,
[miniconda](https://docs.conda.io/en/latest/miniconda.html) is highly recommended. Start by creating a fresh conda
environment (called "myenv" in the example)

    conda create -n myenv python=3.8
    conda activate myenv

Installation with Python versions 3.9 and 3.10 have been tested, but not in production. To run the application on a
local machine, the easiest way is to use [Python'smodule for CGI support](https://docs.python.org/3/library/cgi.html).
Go the parent directory of this repo, rename the repo directory to "cgi-bin" and run

     python -m http.server --bind localhost --cgi PORT

Then, open a web browser and go to http://localhost:PORT/cgi-bin/app.py/. The page will load while required Python
packages are installed. When finished, you will retrieve a message: "Environment has been reset. Try reloading page.".
If properly configured, in [config.cfg](config.cfg) and [idrottonline_feeds.json](idrottonline_feeds.json), the
application should work.

For instructions on how to run on Loopia servers, see https://support.loopia.se/wiki/python/.

## Set up

The services are based on connection to Eventor and a Wordpress site. You need to configure [config.cfg](config.cfg)
and [idrottonline_feeds.json](idrottonline_feeds.json).

### Wordpress site preliminaries

Authentication to Wordpress REST-API is based on JWT, using
[this plugin-in](https://sv.wordpress.org/plugins/jwt-authentication-for-wp-rest-api/), which must be installed on the
Wordpress site. Recommended is to set up an API user, and a dedicated role with limited capabilities, on the Wordpress
site, for member handling requests from this service.

Also cron jobs for calendar and user inventory may be necessary, see more below. To set up a cron job in Wordpress,
[the WP Crontrol Plugin](https://sv.wordpress.org/plugins/wp-crontrol/) simplifies a lot of the work.

To use the example PHP code snippets in these instructions, you must define the following constants in `wp-config.php`
of your Wordpress site:

    define('SERVICE_URL', 'https://yoururl.se');
    define('SERVICE_API_KEY', 'APIKEY');
    define('CALENDAR_FEED_DAYS', 200);

`APIKEY` should be the key specified in [config.cfg](config.cfg) -> ApiSettings -> apikey

### Basic Eventor API configuration

In [config.cfg](config.cfg), you need to give you club's API key and specify ids to club and district. When filled in
correctly, it should be enough for the /members endpoint to work. The other endpoints needs some more configuration on
the Wordpress site.

### Calendar feed

Calendar feeds can be fetched from Eventor, IdrottOnline, and any other source of ICS feeds. These are merged into
a single ICS file, saved to "latest_calendar.ics". In [config.cfg](config.cfg), you need to specify what event types
that will be imported from Eventor.

The serivce has been used with [the calendar plugin AI1EC](https://wordpress.org/plugins/all-in-one-event-calendar/),
which allows regular import of external ICS feeds. Other calendar plugins that allow ICS import should work as well.
To avoid overwriting of the description of a calendar activity that has been imported and then modified in Wordpress,
specify "target_feed" in [config.cfg](config.cfg).

Feeds from IOL must be specified in "idrottonline_feeds.json" on this format:

    [
      {
        "url": "http://idrottonline.se/Calendar/ICalExport.aspx?calendarId=332696&activityTypeIds=&calendarName=Kalendertest&months=6",
        "categories": [
          "IdrottOnline",
          "Ungdom"
        ]
      }
    ]

In this example, categories "IdrottOnline" and "Ungdom" will be added to all activities from this URL, when generating
"latest_calendar.ics". You also need to set "activity_base_url" in [config.cfg](config.cfg) according to your club's
URL.

To fetch activities and save these to 'latest_calendar.ics', a POST request to /calendarfeed/<days> with the correct API
keymust be made. Then, the calendar feed can be imported by GET request to /calendarfeed. To set up
a cron job in Wordpress that makes the POSt request, the following snippet can be inserted into your theme's '
functions.php':

    function call_calendarfeed_update()
    {
    
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, SERVICE_URL . "/calendarfeed/" . CALENDAR_FEED_DAYS);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('X-Api-Key: ' . SERVICE_API_KEY));
    
    
        $server_output = curl_exec($ch);
    
        curl_close($ch);
    }
    
    add_action('calendarfeed_update', 'call_calendarfeed_update');

After adding these lines, you can set up the cron job using WP Crontrol (hook name is calendarfeed_update)

### Registration

At the Wordpress site, you need to set up a user handling member registration requests. Recommended is to delimit its
capabilities to only create/edit users. Specify email and password for this user in [config.cfg](config.cfg) ->
WordpressAPI -> username, password. Also ensure that EventorAPI -> ApiKey, organisation_id & district_id are correct.

The file [parse_settings.json](parse_settings.json) specifies how member information will be retrived from Eventor's
API. Unless the XML
schema in the API response is updated on Eventor's side, there should be no changes to this file and it should be
specified under Member -> parse_settings_file in [config.cfg](config.cfg).

The members created using this service will be given a username which is their Eventor ID

### Member records

Ensure Eventor API configuration is correct. This endpoint does not use Wordpress at all. Note that by having this
service live, all members in the club can access contact information for all other members in the club.

### User inventory

The user inventory endpoint is used for upgrading and downgrading members on the Wordpress site, if their member status
is changed. First, ensure the configuration in section Registration above. Then, specify the users that should not be
checked. For example, admin user and the API user itself in Wordpress -> Reserved users in [config.cfg](config.cfg). The
other users must have a username that equals an Eventor ID which is found in the membership list from Eventor. If a user
is not found, it is degraded to the 'inactive' member type.

To create a cron job on the Wordpress site for calling this endpoint, add the following lines to 'functions.php', and
then add the cron job by using WP Crontrol.

    function call_user_inventory()
    {
    
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, SERVICE_URL . "/inventory");
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('X-Api-Key: ' . SERVICE_API_KEY));
    
    
        $server_output = curl_exec($ch);
    
        curl_close($ch);
    }

    add_action('user_inventory', 'call_user_inventory');

    