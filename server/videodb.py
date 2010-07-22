from imdb import IMDb
import re
import os
import string
import thetvdbapi

# SHOW_MATCH_REGEX="(?P<title>.*)S(?P<season>\d+)E(?P<episode>\d+).*\.(?P<ext>\w+)$"


def gen_db(tv_directory,tv_regex,api_key):
    service = thetvdbapi.TheTVDB(api_key)
    regex = re.compile(tv_regex)
    # shows is a cache of previously found shows.
    shows = { }
    print "The root directory is %s" % tv_directory
    print tv_regex
    for root, dirs, files in os.walk(tv_directory, topdown=True):
        for name in files:
            print name
            info = None
            comp = regex.match(name)
            if comp is not None:
                info = comp.groupdict()
                title = re.sub('\.',' ',info['title']).strip()


                show_info = find_show(service,shows,string.upper(title))

                if show_info:
                    s,e = (info['season'], info['episode'])
                    print "show_info.get_episode(str(int(%s)),str(int(%s)))" % (s , e)
                    episode = show_info.get_episode(str(int(s)),str(int(e)))
                    episode.file_path = os.path.join(root,name)
                    # FIXME: Should get the codec from the file type
                    episode.codec = 'mp4'
                # Now load in the episode information.
            else:
                print u'%s did not match' % name

    return shows

def find_show(service,shows,title):
    if not shows.has_key(title):
        print 'looking for show %s' % title
        showids = service.get_matching_shows(title)

        print 'got %s results' % showids
        (showid,_) = showids[0]
        (showInfo, episodes) = service.get_show_and_episodes(showid)

        shows[title] = showInfo
        elist = {}
        for e in episodes:
            showInfo.add_episode(e)

        return showInfo




def tag(tag,value):
    return u'<%s>%s</%s>\n' % (tag,value,tag)

