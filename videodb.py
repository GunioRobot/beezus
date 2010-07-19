from imdb import IMDb
import re
import os
import string

# SHOW_MATCH_REGEX="b(?P<title>.*)S(?P<season>\d+)E(?P<episode>\d+).*\.(?P<ext>\w+)$"


def gen_db(tv_directory,tv_regex):
    service = IMDb()
    regex = re.compile(tv_regex)
    # shows is a cache of previously found shows.
    shows = { }
    for root, dirs, files in os.walk(tv_directory, topdown=True):
        for name in files:
            info = None
            comp = regex.match(name)
            if comp is not None:
                info = comp.groupdict()
                title = re.sub('\.',' ',info['title']).strip()
                show_info = find_show(service,shows,title)
                if show_info:
                    s,e = (int(info['season']), int(info['episode']))
                    try:
                        elist = show_info['episodes']
                        season = elist[s]
                        episode = season[e]
                        episode['file_path'] = os.path.join(root,name)
                        # FIXME: Should get the codec from the file type
                        episode['codec'] = 'mp4'
                    except:
                        print "Failed on %s - S%s E%s" % (title,s,e)
                        print e

                # Now load in the episode information.
            else:
                print u'%s did not match' % name

    # print_results(shows)
    return shows

def find_show(service,shows,title):
    if not shows.has_key(title):
        showid = service.search_movie(title)
        for match in service.search_movie(title):
            if match['kind'] == 'tv series':
                service.update(match,'episodes')
                shows[title] = match
                return match
            else:
                print "Could not get IMDB results for %s" % title
                return None
    else:
        return shows[title]



def print_results(service,shows):
    str = u'<xml>\n<viddb>\n'
    for i in shows.keys():
        s = shows[i]
        for season, episodes in s['episodes'].iteritems():
            for enum,episode in episodes.iteritems():
                if episode.has_key('file_path'):
                    service.update(episode)
                    str +=  episode_to_xml(episode)
                else:
                    print u'Missing %s %s' % (season,enum)
    str += u'</viddb>\n</xml>\n'
    return str

def episode_to_xml(episode):

            # ('mpaa', 'rating',None),
            # ('director', 'director',format_person_name),
            # ('actors','cast',format_cast),
            # ('description', 'plot outline',None),
            # ('path', 'file_path',None),
            # # ('length', 'runtime'),
            # # ('videocodec', codec),
            # ('poster', 'full-size cover url',None)]

    # print episode.keys()


    str = u'<movie>\n'
    try:
        title = u'Episode %s: %s' % (episode['episode'], episode['canonical title'])
        print title
        str += tag(u'origtitle', title)
        str += tag(u'year', episode['year'])
        # The 'genre' tag is used to encode subcategories
        hierarchy = u'[TV/%s/Season %s]' % (episode['series title'], episode['season'])
        str += tag(u'genre', hierarchy)
        # classification = episode['genre'].append(hierarchy)
        # str += tag('genre', string.join(classification,','))
        # Rating is wrong!
        str += tag(u'mpaa', 'Unrated') # episode['rating'])

        directors = []
        for d in episode['director']:
            directors.append(d['long imdb name'])
            # print d.keys()
        str += tag(u'director',string.join(directors, ','))

        cast = []
        for c in episode['cast']:
            cast.append(c['long imdb name'])
        str += tag(u'actors',string.join(cast[:4], ','))

        str += tag(u'description',episode['plot outline'])
        str += tag(u'path', episode['file_path'])

        str += tag(u'poster', episode['full-size cover url'])

        str += tag(u'videocodec',episode['codec'])

        str += u'</movie>\n'
    except:
        str = "Failed"

    return str

def tag(tag,value):
    return u'<%s>%s</%s>\n' % (tag,value,tag)
