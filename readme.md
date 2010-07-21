Description
-----------

This project contains a server and a client for the Roku video player. It
consists of both a server and a client portion. The server maintains a database
of videos (currently only supporting TV shows). The client is an adaptation of
the videoplayer app supplied with the Roku SDK.

The client talks to the server using a simple URL mapped API, receiving and
parsing results in XML.

Requirements
------------

In addition to the Roku SDK, you'll need a few python support packages:

1. [web.py][webpy] a simple web application framework.

	 [webpy]: http://webpy.org/

2. An API key from [TheTVDB][thetvdb].
	 [thetvdb]: http://thetvdb.com/

3. Probably something else, but I can't remember right now.

Installation
------------

1. Copy the `server/mc.config` file to `/etc/mc.config`. Edit it to include your
	 API key, the path where you want the database to be stored, and the path to
	 a directory where your video files are stored.

	 The database is loaded by using the filename to lookup episode
	 information. It assumes that files are named in the format
	 `<show>.S<season>E<episode>`. If this is not how yours are named, you can
	 modify the `regex` configuration key to suit.

2. The client is installed by navigating to the `client` directory and executing
	 `make install`. This assumes that you have the Roku SDK environment set up
	 correctly, including the `ROKU_DEV_TARGET` environment variable.

Running
-------

The server is started by navigating to the `server` directory and executing `python
videoserver.py`. The first time you do this it will populate the database, which
will take some time. It may be useful, for testing, to only scan a portion of
the video file hierarchy.

Once the server is running, load the client on the Roku box, and navigate away.


TODO
----

This is just a skeleton of a project. It doesn't, currently, even stream
videos. This is because videos must be encoded in an appropriate format, and I
have not done this yet for mine.

