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

from imdb import IMDb

import pickledb
import videodb
from videodb import Movie

render = web.template.render('templates/', cache=False)
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
        return render.movies(web.ctx.db['movies'].values(), web.ctx.app_root,render)


class movie:
    def GET(self, title):
        # print title
        # print web.ctx.db['movies']
        movie = web.ctx.db['movies'][title]
        web.header('Content-Type', 'text/xml')
        return render.movie(movie, web.ctx.app_root)


class shows:
    def GET(self):
        web.header('Content-Type', 'text/xml')
        return render.shows(web.ctx.db['tv'].values(), render)


class seasons:
    def GET(self,show):
        print 'looking for %s' % show

        s = find_show(web.ctx.db['tv'],show)

        if s is None:
            raise web.notfound()


        season_nums = s.episode_list.keys()
        print season_nums
        season_nums.sort(key=int)

        sorted = []
        for season in season_nums:
            sorted.append(s.episode_list[season])

        web.header('Content-Type', 'text/xml')
        return render.seasons(sorted,render)


class episodes:
    def GET(self,show,season):
        s = find_show(web.ctx.db['tv'],show)

        if s is None:
            raise web.notfound()

        web.header('Content-Type', 'text/xml')
        return render.episodes(s.episode_list[season],web.ctx.app_root,render)


class episode:
    def GET(self,show,season,epi):
        print "trying to get a episode"
        s = find_show(web.ctx.db['tv'],show)

        if s is None:
            raise web.notfound()

        print s.episode_list[season]

        ep = s.get_episode(season,epi)
        return render.episode(ep,web.ctx.app_root)


class set_episode_position:
    def POST(self,show,season,episode,position=0):
        data = web.data()
        s = find_show(web.ctx.db['tv'],show)
        if s is None:
            raise web.notfound()

        ep = s.get_episode(season,episode)
        set_position(ep,data)

class set_movie_position:
    def POST(self,show,season,episode,position=0):
        data = web.data()
        movie = web.ctx.db['movies']['title']
        if movie is None:
            raise web.notfound()

        set_position(movie,data)

def set_position(media,pos):
    media.pos = pos
    web.ctx.db.sync()


def play_media(media):
    media.watched = True
    web.ctx.db.sync()

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
        s = find_show(web.ctx.db['tv'],show)
        if s is None:
            raise web.notfound()
        ep = s.get_episode(season,episode)
        play_media(ep)

class play_movie:
    def GET(self,movie):
        m = web.ctx.db['movies'][movie]
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


    cachefile = config.get('global','dbcache')
    db = pickledb.PickleDB(cachefile)

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
        web.ctx.db = db
        web.ctx.static_server = static_server
        web.ctx.path_from = path_from
        web.ctx.path_to = path_to


        # web.ctx.videoindex = index
        web.ctx.imagecache = '/tmp/'
        return handler()

    app.add_processor(_wrapper)
    app.run()

# FIXME: This is dumb, and inefficient. Should use a better way to index it
def find_show(db,show):
    for s in db.values():
        if s.name == show:
            return s

if __name__ == '__main__':
    main()




