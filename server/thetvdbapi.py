"""
thetvdb.com Python API
(c) 2009 James Smith (http://loopj.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from  database import *

import urllib
import datetime
import re

import xml.etree.cElementTree as ET

from sqlobject import *
import sys, os



class TheTVDB(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.mirror_url = "http://www.thetvdb.com"
        self.base_url =  self.mirror_url + "/api"
        self.base_key_url = "%s/%s" % (self.base_url, self.api_key)

    @staticmethod
    def convert_time(time_string):
        """Convert a thetvdb time string into a datetime.time object."""
        time_res = [re.compile(r"\D*(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?.*(?P<ampm>a|p)m.*", re.IGNORECASE), # 12 hour
                    re.compile(r"\D*(?P<hour>\d{1,2}):?(?P<minute>\d{2}).*")]                                     # 24 hour

        for r in time_res:
            m = r.match(time_string)
            if m:
                gd = m.groupdict()

                if "hour" in gd and "minute" in gd and gd["minute"] and "ampm" in gd:
                    hour = int(gd["hour"])
                    if gd["ampm"].lower() == "p":
                        hour += 12

                    return datetime.time(hour, int(gd["minute"]))
                elif "hour" in gd and "ampm" in gd:
                    hour = int(gd["hour"])
                    if gd["ampm"].lower() == "p":
                        hour += 12

                    return datetime.time(hour, 0)
                elif "hour" in gd and "minute" in gd:
                    return datetime.time(int(gd["hour"]), int(gd["minute"]))

        return None

    @staticmethod
    def convert_date(date_string):
        """Convert a thetvdb date string into a datetime.date object."""
        first_aired = None
        try:
            first_aired = datetime.date(*map(int, date_string.split("-")))
        except ValueError:
            pass

        return first_aired

    def get_matching_shows(self, show_name):
        """Get a list of shows matching show_name."""
        get_args = urllib.urlencode({"seriesname": show_name}, doseq=True)
        url = "%s/GetSeries.php?%s" % (self.base_url, get_args)
        data = urllib.urlopen(url)
        show_list = []

        if data:
            try:
                tree = ET.parse(data)
                show_list = [(show.findtext("seriesid"), show.findtext("SeriesName")) for show in tree.getiterator("Series")]
            except SyntaxError:
                pass

        return show_list

    def get_show(self, show_id):
        """Get the show object matching this show_id."""
        url = "%s/series/%s/" % (self.base_key_url, show_id)
        data = urllib.urlopen(url)

        show = None
        try:
            tree = ET.parse(data)
            show_node = tree.find("Series")


            show = Show(show_node, self.mirror_url)
        except SyntaxError:
            pass

        return show

    def get_episode(self, episode_id):
        """Get the episode object matching this episode_id."""
        url = "%s/episodes/%s/" % (self.base_key_url, episode_id)
        data = urllib.urlopen(url)

        episode = None
        try:
            tree = ET.parse(data)
            episode_node = tree.find("Episode")

            episode = TheTVDB.Episode(episode_node, self.mirror_url)
        except SyntaxError:
            pass

        return episode

    def get_show_and_episodes(self, show_id):
        """Get the show object and all matching episode objects for this show_id."""
        url = "%s/series/%s/all/" % (self.base_key_url, show_id)
        data = urllib.urlopen(url)

        show_and_episodes = None
        try:
            tree = ET.parse(data)
            show_node = tree.find("Series")

            show = Show()
            show.load(show_node,self.mirror_url)

            episode_nodes = tree.getiterator("Episode")
            episodes = []
            for episode_node in episode_nodes:
                ep = Episode()
                ep.load(episode_node, self.mirror_url,show)
                episodes.append(ep)

            show_and_episodes = (show, episodes)
        except SyntaxError:
            pass


        return show_and_episodes

    def get_updated_shows(self, period = "day"):
        """Get a list of show ids which have been updated within this period."""
        url = "%s/updates/updates_%s.xml" % (self.base_key_url, period)
        data = urllib.urlopen(url)
        tree = ET.parse(data)

        series_nodes = tree.getiterator("Series")

        return [x.findtext("id") for x in series_nodes]

    def get_updated_episodes(self, period = "day"):
        """Get a list of episode ids which have been updated within this period."""
        url = "%s/updates/updates_%s.xml" % (self.base_key_url, period)
        data = urllib.urlopen(url)
        tree = ET.parse(data)

        episode_nodes = tree.getiterator("Episode")

        return [(x.findtext("Series"), x.findtext("id")) for x in episode_nodes]

    def get_show_image_choices(self, show_id):
        """Get a list of image urls and types relating to this show."""
        url = "%s/series/%s/banners.xml" % (self.base_key_url, show_id)
        data = urllib.urlopen(url)
        tree = ET.parse(data)

        images = []

        banner_data = tree.find("Banners")
        banner_nodes = tree.getiterator("Banner")
        for banner in banner_nodes:
            banner_path = banner.findtext("BannerPath")
            banner_type = banner.findtext("BannerType")
            banner_url = "%s/banners/%s" % (self.mirror_url, banner_path)

            images.append((banner_url, banner_type))

        return images


    def get_season_images(self,show_id):

        regex = re.compile('.*/banners/seasons/(?P<show>\d+)-(?P<season>\d+)(-(?P<num>\d+))?.*')
        images = self.get_show_image_choices(show_id)
        # print images

        season_images = { }
        for banner_path, banner_type  in images:
            if banner_type == 'season':
                print 'Found a banner'

                comp = regex.match(banner_path)
                if comp:
                    info = comp.groupdict()
                    if season_images.has_key(info['season']):
                        season_images[info['season']].append(banner_path)
                    else:
                        season_images[info['season']] = [ banner_path ]

        return season_images







