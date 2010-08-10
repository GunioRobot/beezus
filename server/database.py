import urllib
import datetime
import re

import xml.etree.cElementTree as ET

from sqlobject import *
from sqlobject.sqlbuilder import *
import sys, os

import tmdb


class Genre(SQLObject):
    name = StringCol()
    shows = RelatedJoin('Show')
    @staticmethod
    def createOrFetch(name):
        try:
            return Genre.select(Genre.q.name == name).getOne()
        except:
            return Genre(name=name)

class Show(SQLObject):
    series_id = StringCol(length=1,default=None)
    name = StringCol(default=None)
    overview = StringCol(default=None)
    genres = RelatedJoin('Genre')
    actors = RelatedJoin('Person', addRemoveName='Actor',intermediateTable='show_acted')
    network = StringCol(default=None)
    content_rating = StringCol(default=None)
    rating = StringCol(default=None)
    runtime = StringCol(default=None)
    status = StringCol(default=None)
    language = StringCol(default=None)
    first_aired  = StringCol(default=None)
    poster_url = StringCol(default=None)
    imdb_id = StringCol(default=None)
    tvcom_id = StringCol(default=None)
    zap2it_id = StringCol(default=None)
    last_updated = DateTimeCol(default=None)
    seasons = MultipleJoin('Season',orderBy='season')

    """A python object representing a thetvdb.com show record."""
    def load(self,  node, mirror_url,short_name=None):
        Show.sqlmeta.lazyUpdate=True
        # Main show details
        self.series_id = node.findtext("id")
        self.name = node.findtext("SeriesName")
        self.overview = node.findtext("Overview")
        for g in node.findtext("Genre").split("|"):
            genre = Genre.createOrFetch(g)
            self.addGenre(genre)

        # self.genre = [g for g in node.findtext("Genre").split("|") if g]
        print "XXXXXXX"
        print node.findtext("Actors").split("|")
        for a in node.findtext("Actors").split("|"):
            if a:
                actor = Person.createOrFetch(a)
                self.addActor(actor)

        self.network = node.findtext("Network")
        self.content_rating = node.findtext("ContentRating")
        self.rating = node.findtext("Rating")
        self.runtime = node.findtext("Runtime")
        self.status = node.findtext("Status")
        self.language = node.findtext("Language")

        # Air details
        # self.first_aired = TheTVDB.convert_date(node.findtext("FirstAired"))
        self.airs_day = node.findtext("Airs_DayOfWeek")
        # self.airs_time = TheTVDB.convert_time(node.findtext("Airs_Time"))

        # Main show artwork
        self.banner_url = "%s/banners/%s" % (mirror_url, node.findtext("banner"))
        self.poster_url = "%s/banners/%s" % (mirror_url, node.findtext("poster"))
        self.fanart_url = "%s/banners/%s" % (mirror_url, node.findtext("fanart"))

        # External references
        self.imdb_id = node.findtext("IMDB_ID")
        self.tvcom_id = node.findtext("SeriesID")
        self.zap2it_id = node.findtext("zap2it_id")

        # When this show was last updated
        self.last_updated = datetime.datetime.fromtimestamp(int(node.findtext("lastupdated")))


        # video player specific stuff
        self.episode_list = { }

        self.syncUpdate()
        Show.sqlmeta.lazyUpdate = False


    def __str__(self):
        import pprint
        return pprint.saferepr(self)

    def add_episode(self,episode):
        season = episode.season_number
        try:
            sn = self.episode_list[season]
        except:
            sn = Season(season,self)
            self.episode_list[season] = sn

        sn.add_episode(episode)

    def get_episode(self,season, episode):
        return self.episode_list[season].get_episode(episode)



class Season(SQLObject):
    show = ForeignKey('Show')
    season = IntCol()
    episodes = MultipleJoin('Episode',orderBy='episode_number')
    poster_url = StringCol(default=None)


class Episode(SQLObject):
    episode_id = StringCol(default=None)
    tvdb_show_id = StringCol(default=None)
    name = StringCol(default=None)
    overview = UnicodeCol(default=None)
    season_number = IntCol(default=None)
    episode_number = IntCol(default=None)
    director = StringCol(default=None)
    # guest_stars = RelatedJoin('Person')
    language = StringCol(default=None)
    rating = StringCol(default=None)
    writer = StringCol(default=None)
    show = ForeignKey('Show',default=None)
    season = ForeignKey('Season', default=None)
    file_path = StringCol(default=None)
    poster_url = StringCol(default=None)
    # first_aired = StringCol(default=None)

    """A python object representing a thetvdb.com episode record."""
    def load(self, node, mirror_url, series=None):

        Episode.sqlmeta.lazyUpdate = True
        self.episode_id = node.findtext("id")
        self.tvdb_show_id = node.findtext("seriesid")
        self.name = node.findtext("EpisodeName")
        self.overview = node.findtext("Overview")
        self.season_number = int(node.findtext("SeasonNumber"))
        self.episode_number = int(node.findtext("EpisodeNumber"))
        self.director = node.findtext("Director")
        self.guest_stars = node.findtext("GuestStars")
        self.language = node.findtext("Language")
        self.production_code = node.findtext("ProductionCode")
        self.rating = node.findtext("Rating")
        self.writer = node.findtext("Writer")
        self.show = series
        # set the season
        try:
            self.season = Season.select((Season.q.season==self.season_number) & (Season.q.show==self.show)).getOne()
            # self.season = Season.get(series=series, season=self.season_number)
        except Exception as e:
            print 'XXXXXXXX'
            print e
            self.season = Season(show=series,season=self.season_number)


        # Air date
        from thetvdbapi import TheTVDB
        self.first_aired = TheTVDB.convert_date(node.findtext("FirstAired"))

        # DVD Information
        self.dvd_chapter = node.findtext("DVD_chapter")
        self.dvd_disc_id = node.findtext("DVD_discid")
        self.dvd_episode_number = node.findtext("DVD_episodenumber")
        self.dvd_season = node.findtext("DVD_season")

        # Artwork/screenshot
        self.image = node.findtext("filename")
        if self.image is not None:
            self.poster_url = "%s/banners/%s" % (mirror_url, self.image)
        else:
            self.poster_url = ""
        # Episode ordering information (normally for specials)
        self.airs_after_season = node.findtext("airsafter_season")
        self.airs_before_season = node.findtext("airsbefore_season")
        self.airs_before_episode = node.findtext("airsbefore_episode")

        # Unknown
        self.combined_episode_number = node.findtext("combined_episode_number")
        self.combined_season = node.findtext("combined_season")
        self.absolute_number = node.findtext("absolute_number")
        self.season_id = node.findtext("seasonid")
        self.ep_img_flag = node.findtext("EpImgFlag")

        # External references
        self.imdb_id = node.findtext("IMDB_ID")

        # When this episode was last updated
        self.last_updated = datetime.datetime.fromtimestamp(int(node.findtext("lastupdated")))

        # Handling play history
        self.watched = False
        self.pos = 0
        self.syncUpdate()
        Episode.sqlmeta.lazyUpdate = False

    @staticmethod
    def get_episode(show,season,episode):
        ep = Episode.select((Episode.q.season_number==season) & (Episode.q.episode_number==episode) & (Episode.q.show==show)).getOne()
        return ep

class Movie(SQLObject):
    name = StringCol(default=None)
    overview = UnicodeCol(default=None)
    rating = FloatCol(default=None)
    poster_url = StringCol(default=None)
    actors  = RelatedJoin('Person',addRemoveName='Actor',intermediateTable='movie_acted')
    directors = RelatedJoin('Person',addRemoveName='Director',intermediateTable='movie_directed')
    content_rating = StringCol(default=None)
    watched = BoolCol(default=False)
    pos = IntCol(default=0)
    file_path = StringCol(default=None)


    def load(self,movie):
        Movie.sqlmeta.lazyUpdate = True
        print movie.keys()

        self.name = movie['name']
        self.overview = movie['overview']
        self.rating = float(movie['rating'])
        poster =  movie['images'].posters[0]['cover']
        self.poster_url = poster
        print movie['cast']['actor']
        for a in movie['cast']['actor']:
            actor = Person.createOrFetch(a['name'])
            self.addActor(actor)

        for d in movie['cast']['director']:
            director = Person.createOrFetch(d['name'])
            self.addDirector(director)

        print movie['certification']
        self.content_rating = movie['certification']

        self.watched = False
        self.pos = 0
        self.syncUpdate()
        Movie.sqlmeta.lazyUpdate = False


class Person(SQLObject):
    name = UnicodeCol()
    movies = RelatedJoin('Movie', addRemoveName='ActedMovie', intermediateTable='movie_acted')
    shows = RelatedJoin('Show', addRemoveName='ActedShow', intermediateTable='show_acted')
    directs = RelatedJoin('Movie',addRemoveName='Directed', intermediateTable='movie_directed')


    @staticmethod
    def createOrFetch(name):
        try:
            return Person.select(Person.q.name == name).getOne()
        except:
            return Person(name=name)


def fetch_info(title=None, season_num=None, episode_num=None):
    if not title:
        return None
    print "Looking for show %s" % title
    show = Show.select(Show.q.name==title).getOne()
    if not season_num:
        return show
    season = Season.select((Season.q.show == show) & (Season.q.season == season_num)).getOne()
    if not episode_num:
        print season
        return season
    episode = Episode.select((Episode.q.show == show) & (Episode.q.season == season) & (Episode.q.episode_number == episode_num)).getOne()
    return episode

def main():
    connection_string='sqlite:///tmp/beezus.db'
    connection = connectionForURI(connection_string, debug=True, debugOutput=True)
    sqlhub.processConnection = connection
    try:
        Show.createTable()
        Season.createTable()
        Episode.createTable()
        Movie.createTable()
        Genre.createTable()
        Person.createTable()
    except:
        pass


if __name__ == 'main':
    main()


