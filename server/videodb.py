from database import *

import sys
import getopt
from imdb import IMDb
import re
import os
import string
import thetvdbapi
import imdb
import ConfigParser
import pickledb
from sqlobject import *



class VideoDB:
    def __init__(self,db={}):

        self.tv_directory = ''
        self.tv_regex = ''
        self.tv_api_key = ''
        self.name_map = { }

        self.movie_directory = ''
        self.movie_regex = ''
        self.movie_api_key = ''

        self.interactive = True

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

                    if show_info:
                        s,e = (info['season'], info['episode'])
                        # print
                        # "show_info.get_episode(str(int(%s)),str(int(%s)))" %
                        # (s , e)
                        episode = Episode.get_episode(show_info,int(s), int(e))

                        # episode = show_info.get_episode(str(int(s)),str(int(e)))
                        episode.file_path = os.path.join(root,name)

                        print 'setting file path for %s' % episode.file_path
                        # FIXME: Should get the codec from the file type
                        episode.codec = 'mp4'
                else:
                    print u'%s did not match' % name



    def find_show(self,name):
        print 'Looking for %s' % name
        try:
            return Show.get(self.name_map[name])
        except:
            title = name

            print 'looking for show %s' % title
            showids = self.tv_service.get_matching_shows(title)

            # FIXME: Use a comprehension
            if self.interactive:
                titles = []
                for s,t in showids:
                    titles.append(t)
                idx = get_choice(titles)
            else:
                idx = 0

            (showid,showtitle) = showids[idx]
            print 'You chose %s' % showtitle

            try:
                show = Show.select(Show.q.name==showtitle).getOne()
                self.name_map[name] = show.id
                return show
            except:
                pass

            (showInfo, episodes) = self.tv_service.get_show_and_episodes(showid)
            # print self.tv_service.get_show_image_choices(showid)

            self.name_map[name] = showInfo.id

            # Now fix up the season images
            season_images = self.tv_service.get_season_images(showid)
            print showInfo

            for season in showInfo.seasons:
                # Just grab the first one
                # print season
                try:
                    url = season_images[season.season][0]
                    print "set season image to %s" % url
                except:
                    url = showInfo.poster_url

                season.poster_url = url

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
                        if self.interactive:
                            idx = get_choice(movie_list)
                        else:
                            idx = 0
                        print 'got %s results' % movie_list
                        # for item in movie_list:
                        # # print item
                        try:
                            mi = movie_list[idx]
                            movie = Movie.select(Movie.q.name==mi['title']).getOne()
                            print 'found %s' % movie
                            movie.file_path = os.path.join(root,name)
                        except Exception as e:
                            item = movie_list[idx]
                            self.movie_service.update(item)
                            movie = Movie()
                            movie.load(item)
                            movie.file_path = os.path.join(root,name)
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


    dbfile = config.get('global','db')
    connection = connectionForURI('sqlite://%s' % dbfile)
    print dbfile
    #connection = connectionForURI('sqlite:/:memory:', debug=True)
    sqlhub.processConnection = connection
    try:
        Show.createTable()
        Season.createTable()
        Episode.createTable()
        Movie.createTable()
    except:
        pass


    path = config.get('tv','path')
    regex = config.get('tv','regex')
    apikey = config.get('global','apikey')


    loader = VideoDB()
    loader.tv_directory = path
    loader.tv_regex = regex
    loader.tv_api_key = apikey
    loader.gen_tv_db()

    path = config.get('movies','path')
    regex = config.get('movies','regex')

    loader.movie_directory = path
    loader.movie_regex = regex
    loader.gen_movie_db()


if __name__ == '__main__':
    main()


