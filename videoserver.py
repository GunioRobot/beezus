import string,cgi,time
import sys
import shelve
from os import curdir,sep,path
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import ConfigParser
import web

from imdb import IMDb

import videodb

urls = ('/videos.xml', 'videos',
        '/images/TV/(.*)/.*/poster\.jpg', 'categoryimage',
        '/images/(.*)', 'images')

class videos:
    def GET(self):
        # return "Hello, World"
        return web.ctx.videoindex.encode('latin-1')

class images:
    def GET(self,name):
        return "got an image request: %s" % name

class categoryimage:
    def GET(self,series):
        db = web.ctx.videodb
        if db.has_key(series):
            i = IMDb()
            i.update(db[series])
            image_url = db[series]['full-size cover url']
            return image_url
        else:
            return "Didn't find image for %s season %s" % (series,season)

def main():
    config = ConfigParser.RawConfigParser()
    config.read('/tmp/roxsbox.config')

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
    if shelf.has_key('tv_index'):
        index = shelf['tv_index']
        # print index.encode('latin-1')
    else:
        index = videodb.print_results(service,db)
        # print index.encode('latin-1')
        shelf['tv_index'] = index
        shelf.sync()


    app = web.application(urls, globals())
    # Apparently this is necessary to pass data to the handler:
    def _wrapper(handler):
        web.ctx.videodb = db
        web.ctx.videoindex = index
        return handler()

    app.add_processor(_wrapper)
    app.run()

if __name__ == '__main__':
    main()



