Function makeConfiguration() as Object
  config = CreateObject("roAssociativeArray")

  reg = CreateObject("roRegistry")
  app = CreateObject("roRegistrySection","Beezus")
	if app.Exists("BaseURL") then
    config.url = app.Read("BaseURL")
		return config
  else
	  ' FIXME: Should prompt initial setup here.
	  app.Write("BaseURL", "http://192.168.0.8/Videos/")
		app.Flush()
		return makeConfiguration()
  end if

End Function