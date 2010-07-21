' The load* functions will first fetch data from a url, then they will set the
' display and nextLoader functions for the new data.

' Get a list of all shows
Function loadTV() as Object
  url = config.baseURL + "tv.xml"
  data = genericLoadXMLURL(url,"tv")
	data.nextLoader = loadSeries
  return data
End Function

' Get a list of all movies
Function loadMovies() as Object
  url = config.baseURL + "movies.xml"
  data = genericLoadXMLURL(url,"movies")
	data.nextLoader = loadMovie
  return data
End Function


' This returns a list of seasons for a series
Function loadSeries(series as Object) as Object
	 url = m.config.baseURL + series.Title
   data = genericLoadXMLURL(url,"series")
	 data.nextLoader = loadSeason
	 return data
End Function

' Return a list of episodes in a season
Function loadSeason(season as Object) as Object
	 url = m.config.baseURL + series.Title + "/" + season.season
   data = genericLoadXMLURL(url,"season")
	 data.nextLoader = loadEpisode

	 ' A Season is shown using a episodic style
	 data.posterStyle = "flat-episodic"

	 return data
End Function

' Load the data for a episode
Function loadEpisode(episode as Object) as Object
   ' FIXME: Actually get the show title
   url = m.config.baseURL + "Weeds" + "/" + "1" + "/" + "1"
   data = genericLoadXMLURL(url,"episode")
	 data.preShowScreen = preShowDetail
	 data.showScreen = showDetail
	 data.nextLoader = invalid
	 return data
End Function

' Load the data for a movie
Function loadMovie(movie as Object) as Object
	 url = m.config.baseURL + movie.Title
   data = genericLoadXMLURL(url,"movie")
	 data.preShowScreen = preShowDetail
	 data.showScreen = showDetail
	 data.nextLoader = invalid
	 return data
End Function

Function genericLoadXMLURL(url,t) as Object
  d = loadXMLURL(url, function(xml) return genericLoader(t,xml) end function)
	' Copy the configuration
	d.config = m.config
  return d
End Function

Function loadXMLURL(url as String, loader as Function) as Object
  http = NewHTTP(url)
	Dbg("url: ", http.Http.GetUrl())

  rsp = http.GetToStringWithRetry()

  xml = CreateObject("roXMLElement")
  if not xml.Parse(rsp) then
		 print "Can't parse feed"
		 printXML(xml,10)
		 return invalid
  endif

	res = loader(xml)
  return res
End Function

Function genericLoader(t as String, xml as Object) as Object

  o = makeGenericList(t)
	print "Trying to load"
	printXML(xml,10)

	for each sxml in xml.GetChildElements()
      aa = CreateObject("roAssociativeArray")
			GetXMLintoAA(sxml,aa)
			o.values.Push(aa)
	next

	' printAA(o)

	return o

End Function


Function makeGenericList(t as String) as Object
  o = CreateObject("roAssociativeArray")
  o.type = t
	o.values = CreateObject("roArray",100,true)

  ' The 'display' elements
	o.preShowScreen = genericPreShowScreen
	o.showScreen = genericShowScreen
	o.display = genericDisplay

	return o

End Function