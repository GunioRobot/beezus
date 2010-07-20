' This returns a list of seasons for a series
Function loadSeries(series as Object) as Object
   url = "http://192.168.0.8:8080/Videos/" + series.Title
   data = loadXMLURL(url, seriesLoader)
End Function


Function loadTV(dummy as String) as Integer

  data = loadXMLURL("http://192.168.0.8:8080/Videos/tv.xml", tvLoader)
	data.nextLoader = loadSeries
  return 0

End Function



Function loadXMLURL(url as String, loader as Function) as Object
  http = NewHTTP(url)
	Dbg("url: ", http.Http.GetUrl())

  rsp = http.GetToStringWithRetry()

  xml = CreateObject("roXMLElement")
  if not xml.Parse(rsp) then
		 print "Can't parse feed"
		 return invalid
  endif

	res = loader(xml)
  return res
End Function

Function tvLoader(xml as Object) as Object
  return genericLoader("tv",xml)
  o = CreateObject("roAssociativeArray")
  o.type = "shows"
	o.values = CreateObject("roArray",100,true)

  'PrintAA(o)
   for each sxml in xml.GetChildElements()
      aa = CreateObject("roAssociativeArray")
			GetXMLintoAA(sxml,aa)
			o.values.Push(aa)
	next

	return o
End Function


Function seriesLoader(xml as Object) as Object
  return genericLoader("series",xml)
End Function


Function genericLoader(t as String, xml as Object) as Object
  o = CreateObject("roAssociativeArray")
  o.type = t
	o.values = CreateObject("roArray",100,true)

	for each sxml in xml.GetChildElements()
      aa = CreateObject("roAssociativeArray")
			GetXMLintoAA(sxml,aa)
			o.values.Push(aa)
	next
	return o

End Function
