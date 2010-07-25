Function makeConfiguration() as Object
  config = CreateObject("roAssociativeArray")

  reg = CreateObject("roRegistry")
  app = CreateObject("roRegistrySection","Beezus")

  if app.Exists("BaseURL") then
     config.baseURL = app.Read("BaseURL")
	  	return config
  else
	   ' FIXME: Should prompt initial setup here.
	   app.Write("BaseURL", "http://192.168.0.8:8080/Videos/")
	   app.Flush()
		 return config
  end if

End Function

Function configPreShowScreen() as Object
		screen = CreateObject("roKeyboardScreen")
		port	= CreateObject("roMessagePort")
		screen.SetMessagePort(port)
		screen.SetTitle("Configure server URL")
		screen.SetDisplayText("Set the URL of the media server")
		' screen.SetMaxLength(8)
		screen.AddButton(1, "finished")
		screen.AddButton(2, "back")
    return screen
End Function

Function configShowScreen(screen as Object) as Integer
  config = m.config
  reg = CreateObject("roRegistry")
  app = CreateObject("roRegistrySection","Beezus")
	if app.Exists("BaseURL")
	  url = app.Read("BaseURL")
	else
    url = ""
  end if

		screen.SetText(url)
		screen.Show()

		while true
		  msg = wait(0, screen.GetMessagePort())
			print "message received"
			if type(msg) = "roKeyboardScreenEvent"
        if msg.isScreenClosed()
			    return 0
  		  else if msg.isButtonPressed() then
          ' print "Evt: msg.GetMessage();" idx:"; msg.GetIndex()

	  		  if msg.GetIndex() = 1 then
		   	    url = screen.GetText()
            app.Write("BaseURL", url)
            app.Flush()
					  config.baseURL = url
					  '  print "configuration url";url
            return 0
	 	      endif
         endif
      endif
    end while
End Function