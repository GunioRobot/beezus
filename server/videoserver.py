#!/usr/bin/env python
import string,cgi,time
import sys
import getopt
from os import curdir,sep,path
import re
import urllib
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import ConfigParser
import web
import mimetypes

import videodb
# from videodb import Movie
from sqlobject import *
from sqlobject.sqlbuilder import *
from database import *

imports = {'quote' : urllib.quote }
render = web.template.render('templates/', globals=imports,cache=False)
urls = ('/tv/','shows',
        '/tv/(.+)/(\d+)/(\d+)/play', 'play_episode',
        '/tv/(.+)/(\d+)/(\d+)/position', 'set_episode_position',
        '/tv/(.+)/(\d+)/(\d+)$', 'episode',
        '/tv/(.+)/(\d+)$', 'episodes',
        '/tv/(.+)$', 'seasons',
        # Movies
        '/movies/(.+)/position', 'set_movie_position',
        '/movies/(.+)/play', 'play_movie',
        '/movies/(.+)', 'movie',
        '/movies/', 'movies',
        '.*', 'top'
        )

class movies:
    def GET(self):
        web.header('Content-Type', 'text/xml')
        movies = list(Movie.select())
        return render.movies(movies, web.ctx.app_root,render)


class movie:
    def GET(self, title):
        # print title
        # print web.ctx.db['movies']
        movie = Movie.select(Movie.q.name==title).getOne()
        web.header('Content-Type', 'text/xml')
        return render.movie(movie, web.ctx.app_root)


class shows:
    def GET(self):
        web.header('Content-Type', 'text/xml')
        shows = list(Show.select())
        return render.shows(shows, render)


class seasons:
    def GET(self,show):
        # FIXME: Sort the seasons.
        web.header('Content-Type', 'text/xml')
        return render.seasons(fetchInfo(show).seasons,render)


class episodes:
    def GET(self,show,season):
        web.header('Content-Type', 'text/xml')
        return render.episodes(fetchInfo(show,int(season)),web.ctx.app_root,render)


class episode:
    def GET(self,show,season,epi):
        ep = fetchInfo(show,int(season),int(epi))
        return render.episode(ep,web.ctx.app_root)


class set_episode_position:
    def POST(self,show,season,episode,position=0):

        s = Show.select(Show.q.name==show).getOne()
        if s is None:
            raise web.notfound()

        ep = fetchInfo(show,int(season),int(epi))
        ep.pos = int(position)

class set_movie_position:
    def POST(self,title,position=0):
        movie = Movie.select(Movie.q.name == title).getOne()

        if movie is None:
            raise web.notfound()
        movie.pos = int(position)


def play_media(media):
    media.watched = True
    if web.ctx.static_server:
        url = re.sub(web.ctx.path_from,web.ctx.path_to,media.file_path)
        # print 'Playing %s' % url
        raise web.seeother(url)
    else:
        mime_type = mimetypes.guess_type(media.file_path)[0] or 'application/octet-stream'
        web.header("Content-Type", mime_type)
        static_file = open(media.file_path, 'rb')
        # print static_file.size()
        return static_file


class play_episode:
    def GET(self,show,season,episode):
        ep = fetchInfo(show,int(season),int(epi))
        play_media(ep)

class play_movie:
    def GET(self,movie):
        m = Movie.select(Movie.q.name == movie).getOne()
        if m is None:
            raise web.notfound()
        play_media(m)




def main(argv=None):
    """
    Serve a video database.
    """
    if argv is None:
        argv = sys.argv


    # handling options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help","config="])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    config_file = '/etc/mc.config'
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-c", "--config"):
            config_file = a

    # read in configuration
    print config_file
    config = ConfigParser.RawConfigParser()
    config.read(config_file)


    config = ConfigParser.RawConfigParser()
    config.read(config_file)
    path = config.get('tv','path')
    regex = config.get('tv','regex')
    apikey = config.get('global','apikey')


    dbfile = config.get('global','db')
    connection = connectionForURI('sqlite://%s' % dbfile)
    print dbfile
    #connection = connectionForURI('sqlite:/:memory:', debug=True)
    sqlhub.processConnection = connection


    # URL modifications
    app_root = config.get('global','app_root')

    static_server = config.getboolean('global','static_server')
    if static_server:
        path_from = config.get('global','path_from')
        path_to = config.get('global', 'path_to')
    else:
        path_from = None
        path_to = None


    # print videodb.gen_tv_xml(db).encode('latin-1')

    app = web.application(urls, globals())
    # Apparently this is necessary to pass data to the handler:
    def _wrapper(handler):
        web.ctx.app_root = app_root
        web.ctx.static_server = static_server
        web.ctx.path_from = path_from
        web.ctx.path_to = path_to


        # web.ctx.videoindex = index
        web.ctx.imagecache = '/tmp/'
        return handler()

    app.add_processor(_wrapper)
    app.run()

if __name__ == '__main__':
    main()


