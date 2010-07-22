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

urls = ('/Videos/tv.xml', 'shows',
        '/Videos/(.*)/(.*)/(.*)/play', 'play_episode',
        '/Videos/(.*)/(.*)/(.*)$', 'episode',
        '/Videos/(.*)/(.*)$', 'episodes',
        '/Videos/(.*)$', 'seasons')


class shows:
    def GET(self):
        # return "Hello, World"
        str = "<tv>\n"
        for s in web.ctx.videodb.values():
            str += s.render_xml()
        str += "</tv>"
        return str


class seasons:
    def GET(self,show):
        print 'looking for %s' % show

        s = find_show(web.ctx.videodb,show)

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
        s = find_show(web.ctx.videodb,show)

        if s is None:
            raise web.notfound()

        str = u'<season>'
        for e in s.episode_list[season].episodes.values():
            str += e.render_xml(web.ctx.app_root)
        str += u'</season>'
        return str

class episode:
    def GET(self,show,season,epi):
        print "trying to get a episode"
        s = find_show(web.ctx.videodb,show)

        if s is None:
            raise web.notfound()

        print s.episode_list[season]

        ep = s.get_episode(season,epi)
        return  ep.render_xml(web.ctx.app_root)

class play_episode:
    def GET(self,show,season,episode):
        s = find_show(web.ctx.videodb,show)
        if s is None:
            raise web.notfound()

        ep = s.get_episode(season,episode)

        if web.ctx.static_server:
            url = re.sub(web.ctx.path_from,web.ctx.path_to,ep.file_path)
            raise web.seeother(url)
        else:
            mime_type = mimetypes.guess_type(ep.file_path)[0] or 'application/octet-stream'
            web.header("Content-Type", mime_type)
            static_file = open(ep.file_path, 'rb')
            return static_file




def main():
    config = ConfigParser.RawConfigParser()
    config.read('/etc/mc.config')

    cachefile = config.get('global','dbcache')
    shelf = shelve.open(cachefile)

    if shelf.has_key('tv'):
        print "Opening the database"
        db = shelf['tv']
    else:
        db = videodb.gen_db(path,regex,apikey)
        shelf['tv'] = db
        shelf.sync()

    path = config.get('tv','path')
    regex = config.get('tv','regex')
    apikey = config.get('global','apikey')

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
        web.ctx.videodb = db
        web.ctx.static_server = static_server
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
