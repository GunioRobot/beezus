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

urls = ('/Videos/videos.xml', 'videos',
        '/Videos/http://(.*)', 'images',
        '/Videos/images/TV/(.*)/.*/poster\.jpg', 'categoryimage',
        '/Videos/images/(.*)', 'images')


class videos:
    def GET(self):
        # return "Hello, World"
        return web.ctx.videoindex.encode('ascii','ignore')

class images:
    def GET(self,image_url):
        url = 'http://' +image_url
        (b,f) = path.split('http://' + url)
        # web.notfound()
        #print "looking for %s" % image_url

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
        web.ctx.imagecache = '/tmp/'
        return handler()

    app.add_processor(_wrapper)
    app.run()

if __name__ == '__main__':
    main()



