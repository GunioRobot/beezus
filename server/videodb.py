from imdb import IMDb
import re
import os
import string
import thetvdbapi
import imdb
import ConfigParser
import shelve

def gen_tv_db(tv_directory,tv_regex,api_key, shows={}):
    service = thetvdbapi.TheTVDB(api_key)
    regex = re.compile(tv_regex)
    # shows is a cache of previously found shows.
    print "The root directory is %s" % tv_directory
    # print tv_regex
    for root, dirs, files in os.walk(tv_directory, topdown=True):
        for name in files:
            info = None
            comp = regex.match(name)
            if comp is not None:
                info = comp.groupdict()
                title = re.sub('\.',' ',info['title']).strip()
                show_info = find_show(service,shows,string.upper(title))

                if show_info:
                    s,e = (info['season'], info['episode'])
                    # print "show_info.get_episode(str(int(%s)),str(int(%s)))" % (s , e)
                    episode = show_info.get_episode(str(int(s)),str(int(e)))
                    episode.file_path = os.path.join(root,name)

                    print 'setting file path for %s' % episode.file_path
                    # FIXME: Should get the codec from the file type
                    episode.codec = 'mp4'
                # Now load in the episode information.
            else:
                print u'%s did not match' % name

    return shows

def find_show(service,shows,title):
    print 'Looking for %s' % title
    if not shows.has_key(title):
        print 'looking for show %s' % title
        showids = service.get_matching_shows(title)

        print 'got %s as results' % showids
        (showid,_) = showids[0]
        (showInfo, episodes) = service.get_show_and_episodes(showid)
        # print service.get_show_image_choices(showid)

        shows[title] = showInfo
        elist = {}
        for e in episodes:
            showInfo.add_episode(e)

        # Now fix up the season images
        season_images = service.get_season_images(showid)

        for (season, season_info) in showInfo.episode_list.iteritems():
            # Just grab the first one
            try:
                url = season_images[season][0]
            except:
                url = showInfo.poster_url

            season_info.poster_url = url
            # print url

        return showInfo

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

    def render_xml(self,server_url=None):
        str = u''
        str += tag('ContentType',u'movie')
        str += tag('Title', self.name)
        str += tag('ShortDescriptionLine1', self.name)
        # str += tag('ShortDescriptionLine2', u'Season %s Episode %s' % (self.season_number, self.episode_number ))
        str += tag('Description', self.overview)
        if self.rating:
            str += tag('StarRating', float(self.rating) * 10)
        str += tag('Rating',self.content_rating)
        str += tag('HDPosterURL', self.poster_url)
        # str += tag('ReleaseDate', self.release_date)

        # FIXME: Generate the stream properly
        try:
            url = '%s/movies/%s/play' % (server_url,self.name)

            stream = tag('url', url)
            stream += tag('bitrate', 200)
            stream += tag('quality', 'false')
            #stream += tag('contentid', self.id)
            stream += tag('stickyredirects', 'true')
            str += tag('stream',stream)
        except:
            pass

        try:
            actors = ''
            for a in self.actors[:2]:
                actors += tag('actor',a)

            tag('actors',actors)
            str += tag('actors',actors)
        except Exception as e:
            print e

        str += tag('Watched', self.watched)
        str += tag('Position',self.pos)

        return tag('movie',str)

def tag(tag,value):
    return u'<%s>%s</%s>\n' % (tag,value,tag)


def main():
    config = ConfigParser.RawConfigParser()
    config.read('/etc/mc.config')


    cachefile = config.get('global','dbcache')
    shelf = shelve.open(cachefile)

    if not shelf.has_key('tv'):
        shelf['tv'] = { }

    if not shelf.has_key('movies'):
        shelf['movies'] = { }

    path = config.get('tv','path')
    regex = config.get('tv','regex')
    apikey = config.get('global','apikey')
    shelf['tv'] = gen_tv_db(path,regex,apikey,shelf['tv'])

    path = config.get('movies','path')
    regex = config.get('movies','regex')
    shelf['movies'] = gen_movie_db(path,regex,shelf['movies'])

    shelf.sync()
    shelf.close()

def gen_movie_db(movie_directory,movie_regex,api_key, movies={}):
    files = ['Shrek']
    service = imdb.IMDb()
    regex = re.compile(movie_regex)

    for root, dirs, files in os.walk(movie_directory, topdown=True):
        for name in files:
            info = None
            comp = regex.match(name)
            if comp is not None:
                info = comp.groupdict()
                title = re.sub('\.',' ',info['title']).strip()
                print 'Checking %s' % title
                try:
                    movie = movie_directory['title']
                except:
                    movie_list = service.search_movie(title)
                    item = movie_list[0]
                    service.update(item)
                    movie = Movie(item)

                movie.file_path = os.path.join(root,name)
                movies[title] = movie
            else:
                print u'%s does not match' % name

            return movies

if __name__ == '__main__':
    main()


