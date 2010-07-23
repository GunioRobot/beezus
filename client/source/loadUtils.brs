' The load* functions will first fetch data from a url, then they will set the
' display and nextLoader functions for the new data.

' Get a list of all shows
Function loadTV() as Object

  ' printAA(m)

  url = m.config.baseURL + "tv.xml"
  data = genericLoadXMLURL(m.config,url)
	data.nextLoader = loadSeries
	'print "Loaded"
	'printAA(data)
  return data
End Function

' Get a list of all movies
Function loadMovies() as Object
  url = m.config.baseURL + "movies.xml"
  data = genericLoadXMLURL(m.config,url)
	data.nextLoader = loadMovie
  return data
End Function


' This returns a list of seasons for a series
Function loadSeries(series as Object) as Object
	 url = m.config.baseURL + series.Title
   data = genericLoadXMLURL(m.config,url)
	 data.nextLoader = loadSeason
	 return data
End Function

' Return a list of episodes in a season
Function loadSeason(season as Object) as Object
	 url = m.config.baseURL + m.parent.Title + "/" + season.season
   data = genericLoadXMLURL(m.config,url)
	 data.nextLoader = loadEpisode

	 ' A Season is shown using a episodic style
	 data.posterStyle = "flat-episodic"

	 return data
End Function

' Load the data for a episode
Function loadEpisode(episode as Object) as Object
   ' FIXME: Actually get the show title
	 ' printAA(episode)
	 ' print m.config.baseURL
	 ' print m.config.baseURL + episode.series
	 ' print m.config.baseURL + episode.series + "/"
	 ' print m.config.baseURL + episode.series + "/" + episode.season
	 ' print m.config.baseURL + episode.series + "/" + episode.season + "/"
	 ' print m.config.baseURL + episode.series + "/" + episode.season + "/" + str(episode.episode)

	 url = m.config.baseURL + episode.series +  "/" + episode.season + "/" + episode.episode

   ' data = genericLoadXMLURL(m.config,url)

	 data = loadXMLURL(url,episodeLoader)
	 ' printAA(data)
	 data.config = m.config

	 data.preShowScreen = preShowDetail
	 data.showScreen = showDetail
	 data.nextLoader = invalid
	 return data
End Function

' Load the data for a movie
Function loadMovie(movie as Object) as Object
	 url = m.config.baseURL + movie.Title
   data = genericLoadXMLURL(m.config,url)
	 data.preShowScreen = preShowDetail
	 data.showScreen = showDetail
	 data.nextLoader = invalid
	 return data
End Function

Function genericLoadXMLURL(config as Object,url as String) as Object
	print "Loading "; url
  d = loadXMLURL(url, genericLoader)
	' printAA(d)

	' Copy the configuration
	d.config = config
  return d
End Function

Function loadXMLURL(url as String, loader as Function) as Object
  http = NewHTTP(url)
	Dbg("url: ", http.Http.GetUrl())

  rsp = http.GetToStringWithRetry()

  xml = CreateObject("roXMLElement")
  if not xml.Parse(rsp) then
		 print "Can't parse feed"
		 ' printXML(xml,10)
		 return invalid
  endif

	res = loader(xml)
  return res

End Function

Function genericLoader(xml as Object) as Object

  o = makeGenericList(xml.getName())
	' print "Trying to load"
	' printXML(xml,10)

	for each sxml in xml.GetChildElements()
      aa = CreateObject("roAssociativeArray")
			GetXMLintoAA(sxml,aa)
			o.values.Push(aa)
	next

	return o

End Function

Function episodeLoader( xml as Object) as Object
  o = makeGenericObject("episode")
	printXML(xml,10)
	GetXMLintoAA(xml,o)

	list = CreateObject("roArray", 100, true)
	for each s in xml.stream
	  aa = { }
		GetXMLintoAA(s,aa)
		aa.stickyredirects = strToBool(aa.stickyredirects)
		list.push(aa)
	next
	o.streams = list

	list = CreateObject("roArray", 4, true)
	for each actor in xml.actors.actor
	  list.push(actor.GetBody())
	next
	o.actors = list

	print o.watched
 	o.watched = strToBool(o.watched)

	printAA(o)
  return o

End Function

Function movieLoader( xml as Object) as Object
  o = makeGenericObject("movie")
	GetXMLintoAA(xml,o)
  return o
End Function

Function makeGenericObject(t as String) as Object
  o = CreateObject("roAssociativeArray")
	o.type = t

  ' The 'display' elements
	o.preShowScreen = genericPreShowScreen
	o.showScreen = genericShowScreen
	o.display = genericDisplay

	return o

End Function

Function makeGenericList(t as String) as Object
  o = makeGenericObject(t)
	o.values = CreateObject("roArray",100,true)
	return o

End Function