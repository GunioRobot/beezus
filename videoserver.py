import string,cgi,time
import sys
import shelve
from os import curdir,sep,path
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import ConfigParser
# import web

from imdb import IMDb

import videodb


class VideoHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/video.xml':
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            self.wfile.write(self.server.index.encode('latin-1'))
            return
        else:
            self.send_response(404)
            print "Could not serve %s" % self.path

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

    try:
        server = HTTPServer(('localhost',8888), VideoHandler)
        server.index = index
        print 'started httpserver...'
        server.serve_forever()
    except:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

