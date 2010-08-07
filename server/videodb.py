import sys
import getopt
from imdb import IMDb
import re
import os
import string
import thetvdbapi
import imdb
import ConfigParser
import shelve


class Movie:
    def __init__(self,movie):
        self.name = movie['title']
        self.overview = movie['plot outline']
        self.rating = movie['rating']
        self.poster_url = movie['full-size cover url']
        # self.release_date = movie[' ']
        #self.id = movie['id']
        self.actors = movie['actors']
        self.directors = movie['director']
        for c in movie['certificates']:
            if c[:3] == 'USA':
                self.content_rating = c[4:]


        self.watched = False
        self.pos = 0


class VideoDB:
    def __init__(self,db={}):

        self.db = db
        print self.db.keys()

        self.tv_directory = ''
        self.tv_regex = ''
        self.tv_api_key = ''
        self.name_map = { }

        self.movie_directory = ''
        self.movie_regex = ''
        self.movie_api_key = ''

    def gen_tv_db(self):
        self.tv_service = thetvdbapi.TheTVDB(self.tv_api_key)
        regex = re.compile(self.tv_regex)

        print "The root directory is %s" % self.tv_directory
        # print tv_regex
        for root, dirs, files in os.walk(self.tv_directory, topdown=True):
            for name in files:
                info = None
                comp = regex.match(name)
                if comp is not None:
                    info = comp.groupdict()
                    title = re.sub('\.',' ',info['title']).strip()
                    show_info = self.find_show(string.upper(title))
                    print self.db['tv']

                    if show_info:
                        s,e = (info['season'], info['episode'])
                        # print "show_info.get_episode(str(int(%s)),str(int(%s)))" % (s , e)
                        episode = show_info.get_episode(str(int(s)),str(int(e)))
                        episode.file_path = os.path.join(root,name)

                        print 'setting file path for %s' % episode.file_path
                        # FIXME: Should get the codec from the file type
                        episode.codec = 'mp4'
                else:
                    print u'%s did not match' % name

        print self.db['tv'].keys()


    def find_show(self,name):
        print 'Looking for %s' % name
        try:
            title = self.name_map[name]
        except:
            title = name

        if not self.db['tv'].has_key(title):
            print 'looking for show %s' % title
            showids = self.tv_service.get_matching_shows(title)

            # print 'got %s results' % s.length()
            # FIXME: Use a comprehension
            titles = []
            for s,t in showids:
                titles.append(t)
            idx = get_choice(titles)

            (showid,showtitle) = showids[idx]
            print 'You chose %s' % showtitle
            (showInfo, episodes) = self.tv_service.get_show_and_episodes(showid)
            # print service.get_show_image_choices(showid)
            # print showInfo.name



            # Absolutely no idea why this is necessary
            # self.db['tv'][title] = showInfo
            title = showInfo.name
            self.name_map[name] = title

            tv = self.db['tv']
            tv[title] = showInfo
            self.db['tv'] = tv

            print 'tv %s' % tv
            print 'db %s' % self.db

            elist = {}
            for e in episodes:
                showInfo.add_episode(e)

            # Now fix up the season images
            season_images = self.tv_service.get_season_images(showid)

            for (season, season_info) in showInfo.episode_list.iteritems():
                # Just grab the first one
                try:
                    url = season_images[season][0]
                except:
                    url = showInfo.poster_url

                season_info.poster_url = url
            return showInfo



    def gen_movie_db(self):
        self.movie_service = imdb.IMDb()
        regex = re.compile(self.movie_regex)

        for root, dirs, files in os.walk(self.movie_directory, topdown=True):
            for name in files:
                info = None
                comp = regex.match(name)
                if comp is not None:
                    info = comp.groupdict()
                    title = re.sub('\.',' ',info['title']).strip()
                    print 'Checking %s' % title
                    try:
                        movie = self.db['movies'][title]
                    except:
                        movie_list = self.movie_service.search_movie(title)
                        idx = get_choice(movie_list)
                    # print 'got %s results' % movie_list
                    # for item in movie_list:
                    # print item

                    item = movie_list[idx]
                    self.movie_service.update(item)
                    movie = Movie(item)

                    movie.file_path = os.path.join(root,name)

                    # self.db['movies'][title] = movie
                    # No idea why this is necessary
                    movies = self.db['movies']
                    movies[movie.name] = movie
                    self.db['movies'] = movies

                else:
                    print u'%s does not match' % name

def get_choice(choices):
    num = 0
    if len(choices) > 1:
        i = 0
        for c in choices:
            print '%s: %s' % (i,c)
            i += 1
        print "selection: [0]: "
        num = raw_input()

        try:
            num = int(num)
        except:
            num = 0

    print 'Chose %s' % num
    return num

def main(argv=None):
    """
    Build a video database.
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
    config_file = '/etc/beezus.cfg'
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-c", "--config"):
            config_file = a

    # read in configuration
    config = ConfigParser.RawConfigParser()
    config.read(config_file)


    cachefile = config.get('global','dbcache')
    shelf = shelve.open(cachefile)

    if not shelf.has_key('tv'):
        shelf['tv'] = { }

    if not shelf.has_key('movies'):
        shelf['movies'] = { }

    path = config.get('tv','path')
    regex = config.get('tv','regex')
    apikey = config.get('global','apikey')

    loader = VideoDB(shelf)
    loader.tv_directory = path
    loader.tv_regex = regex
    loader.tv_api_key = apikey
    loader.gen_tv_db()
    # shelf['tv'] = gen_tv_db(path,regex,apikey,shelf['tv'])

    path = config.get('movies','path')
    regex = config.get('movies','regex')

    loader.movie_directory = path
    loader.movie_regex = regex
    loader.gen_movie_db()

    print loader.db
    shelf.sync()
    shelf.close()

if __name__ == '__main__':
    main()


