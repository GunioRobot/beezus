import string,cgi,time
import sys
import shelve
from os import curdir,sep,path
import urllib
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import ConfigParser
import web
import mimetypes

from imdb import IMDb

import videodb

urls = ('/Videos/tv.xml', 'shows',
        '/Videos/(.*)/(.*)/(.*)', 'get_episode',
        '/Videos/(.*)/(.*)$', 'episodes',
        '/Videos/(.*)$', 'seasons',
        '/Videos/http://(.*)', 'images',
        '/Videos/images/TV/(.*)/.*/poster\.jpg', 'categoryimage',
        '/Videos/images/(.*)', 'images')


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
        for season in s.episode_list.values():
            str += season.render_xml()

        str += u'</series>\n'
        return str

class episodes:
    def GET(self,show,season):
        s = find_show(web.ctx.videodb,show)

        if s is None:
            raise web.notfound()

        str = u'<season>'
        for e in s.episode_list[season].episodes.values():
            print e
            str += e.render_xml()

        str += u'</season>'
        return str

class get_episode:
    def GET(self,show,season,epi):
        print "trying to get a episode"
        s = find_show(web.ctx.videodb,show)

        if s is None:
            raise web.notfound()

        print s.episode_list[season]

        ep = s.get_episode(season,epi)
        str = u'<episode>'
        str += ep.render_xml()
        str += u'</episode>'
        return str




class images:
    def GET(self,image_url):
        url = 'http://' +image_url
        (b,f) = path.split('http://' + url)

        #try:
        cachedfile = path.join(web.ctx.imagecache, f)
        urllib.urlretrieve(url,cachedfile)
        mime_type = mimetypes.guess_type(cachedfile)[0] or 'application/octet-stream'
        web.header("Content-Type", mime_type)
        static_file = open(cachedfile, 'rb')
        #web.ctx.output = static_file
        return static_file
        # except:
        #     web.notfound()



class categoryimage:
    def GET(self,series):
        web.notfound()
        db = web.ctx.videodb
        if db.has_key(series):
            i = IMDb()
            i.update(db[series])
            image_url = db[series]['full-size cover url']


            (b,f) = path.split(image_url)

            #try:
            cachedfile = path.join(web.ctx.imagecache, f)
            urllib.urlretrieve(image_url,cachedfile)
            mime_type = mimetypes.guess_type(cachedfile)[0] or 'application/octet-stream'
            web.header("Content-Type", mime_type)
            static_file = open(cachedfile, 'rb')
            web.ctx.output = static_file
            # except:
            #     web.notfound()

        else:
            return "Didn't find image for %s season %s" % (series,season)

def main():
    config = ConfigParser.RawConfigParser()
    config.read('/tmp/mc.config')

    cachefile = config.get('global','dbcache')
    shelf = shelve.open(cachefile)

    if shelf.has_key('tv'):
        db = shelf['tv']
    else:
        path = config.get('tv','path')
        regex = config.get('tv','regex')
        db = videodb.gen_db(path,regex)
        shelf['tv'] = db
        shelf.sync()

    service = IMDb()
    # if shelf.has_key('tv_index'):
    #index = shelf['tv_index']
    # print index.encode('latin-1')
    #else:
    # index = videodb.gen_tv_xml(db)
    # shelf['tv_index'] = index
    # shelf.sync()


    # print videodb.gen_tv_xml(db).encode('latin-1')

    app = web.application(urls, globals())
    # Apparently this is necessary to pass data to the handler:
    def _wrapper(handler):
        web.ctx.videodb = db
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
