import string,cgi,time
import sys
import shelve
from os import curdir,sep,path
import re
import urllib
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import ConfigParser
import web
import mimetypes

from imdb import IMDb

import videodb
from videodb import Movie

urls = ('/Videos/tv.xml', 'shows',
        '/Videos/tv/','shows',
        '/Videos/tv/(.+)/(\d+)/(\d+)/play', 'play_episode',
        '/Videos/tv/(.+)/(\d+)/(\d+)/position', 'set_episode_position',
        '/Videos/tv/(.+)/(\d+)/(\d+)$', 'episode',
        '/Videos/tv/(.+)/(\d+)$', 'episodes',
        '/Videos/tv/(.+)$', 'seasons',
        # Movies
        '/Videos/movies/(.+)/position', 'set_movie_position',
        '/Videos/movies/(.+)/play', 'play_movie',
        '/Videos/movies/(.+)', 'movie',
        '/Videos/movies/', 'movies',
        )

class movies:
    def GET(self):
        str = "<movies>\n"
        for m in web.ctx.db['movies'].values():
            str += m.render_xml(web.ctx.app_root)
        str += "</movies>"
        return str

class movie:
    def GET(self, title):
        movie = web.ctx.db['movies'][title]
        return movie.render_xml(web.ctx.app_root)



class shows:
    def GET(self):
        # return "Hello, World"
        str = "<tv>\n"
        for s in web.ctx.db['tv'].values():
            str += s.render_xml()
        str += "</tv>"
        return str


class seasons:
    def GET(self,show):
        print 'looking for %s' % show

        s = find_show(web.ctx.db['tv'],show)

        if s is None:
            raise web.notfound()

        print 'found %s' % s
        str = u'<series>\n'
        season_nums = s.episode_list.keys()
        season_nums.sort(key=int)

        for season in season_nums:
            str += s.episode_list[season].render_xml()

        str += u'</series>\n'
        return str

class episodes:
    def GET(self,show,season):
        s = find_show(web.ctx.db['tv'],show)

        if s is None:
            raise web.notfound()

        str = u'<season>'
        episode_nums = s.episode_list[season].episodes.keys()
        episode_nums.sort(key=int)

        for e in episode_nums:
            str += s.episode_list[season].episodes[e].render_xml(web.ctx.app_root)
        str += u'</season>'
        return str

class episode:
    def GET(self,show,season,epi):
        print "trying to get a episode"
        s = find_show(web.ctx.db['tv'],show)

        if s is None:
            raise web.notfound()

        print s.episode_list[season]

        ep = s.get_episode(season,epi)
        return  ep.render_xml(web.ctx.app_root)

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
        print 'Playing %s' % url
        raise web.seeother(url)
    else:
        mime_type = mimetypes.guess_type(media.file_path)[0] or 'application/octet-stream'
        web.header("Content-Type", mime_type)
        static_file = open(media.file_path, 'rb')
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




def main():
    config = ConfigParser.RawConfigParser()
    config.read('/etc/mc.config')
    path = config.get('tv','path')
    regex = config.get('tv','regex')
    apikey = config.get('global','apikey')


    cachefile = config.get('global','dbcache')
    db = shelve.open(cachefile)

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


if __name__ == '__main__':
    main()


# FIXME: This is dumb, and inefficient. Should use a better way to index it
def find_show(db,show):
    for s in db.values():
        if s.name == show:
            return s
