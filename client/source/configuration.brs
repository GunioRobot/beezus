Function makeConfiguration() as Object
  config = CreateObject("roAssociativeArray")

  reg = CreateObject("roRegistry")
  app = CreateObject("roRegistrySection","Beezus")
	if app.Exists("BaseURL") then
	  app.Write("BaseURL", "http://192.168.0.8:8080/Videos/")
		app.flush()
    config.baseURL = app.Read("BaseURL")
		return config
  else
	  ' FIXME: Should prompt initial setup here.
	  app.Write("BaseURL", "http://192.168.0.8:8080/Videos/")
		app.Flush()
		return makeConfiguration()
  end if

End Function