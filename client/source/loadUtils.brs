' Get a list of all shows
Function loadTV() as Object
  data = loadXMLURL("http://192.168.0.8:8080/Videos/tv.xml", tvLoader)
	data.nextLoader = loadSeries
  return data
End Function

' This returns a list of seasons for a series
Function loadSeries(series as Object) as Object
   url = "http://192.168.0.8:8080/Videos/" + series.Title
   data = loadXMLURL(url, seriesLoader)
	 data.nextLoader = loadSeason
	 return data
End Function

Function loadSeason(season as Object) as Object
   ' FIXME: Season number is hard coded. Shouldn't be.
   url = "http://192.168.0.8:8080/Videos/" + season.Title + "/" + season.season
   data = loadXMLURL(url, seasonLoader)
	 data.nextLoader = loadEpisode
	 return data
End Function

Function loadEpisode(episode as Object) as Object
   ' FIXME: Actually get the show title
   ' url = "http://192.168.0.8:8080/Videos/" + "Weeds" + "/" + episode.season + "/" + episode.number
   url = "http://192.168.0.8:8080/Videos/" + "Weeds" + "/" + "1" + "/" + "1"
   data = loadXMLURL(url, episodeLoader)
	 data.preShowScreen = preShowDetail
	 data.showScreen = showDetail
	 data.nextLoader = invalid
	 return data
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

Function tvLoader(xml as Object) as Object
  return genericLoader("tv",xml)
End Function

Function seasonLoader(xml as Object) as Object
  data = genericLoader("season", xml)
  data.posterStyle = "flat-episodic"
	return data

End Function

Function seriesLoader(xml as Object) as Object
  return genericLoader("series",xml)
End Function

Function episodeLoader(xml as Object) as Object
  return genericLoader("episode", xml)
End Function


Function genericLoader(t as String, xml as Object) as Object
  o = CreateObject("roAssociativeArray")
  o.type = t
	o.values = CreateObject("roArray",100,true)

	print "Trying to load"
	printXML(xml,10)

	for each sxml in xml.GetChildElements()
      aa = CreateObject("roAssociativeArray")
			GetXMLintoAA(sxml,aa)
			o.values.Push(aa)
	next

	printAA(o)

	o.preShowScreen = genericPreShowScreen
	o.showScreen = genericShowScreen
	o.display = genericDisplay

	return o


End Function
