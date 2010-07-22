Function genericPreShowScreen() As Object

  port=CreateObject("roMessagePort")
  screen=CreateObject("roPosterScreen")
  screen.SetMessagePort(port)
  ' TODO: Add in the breadcrumbs from the data

	' TODO: Get the style from the data
	if m.posterStyle <> invalid then
		screen.SetListStyle(m.posterStyle)
	else
		screen.SetListStyle("arched-portrait")
  end if
	return screen
End Function


Function genericShowScreen(screen) As Integer
  ' print m.values
  screen.SetContentList(m.values)
	screen.SetFocusedListItem(0)
	screen.Show()

  ' The event loop
	while true
    msg = wait(0,screen.GetMessagePort())
    if type(msg) = "roPosterScreenEvent" then
      if msg.isListItemSelected() then
			  idx = msg.GetIndex()
				data = m.values[idx]
				newdata = m.nextLoader(data)
				' printAA(newdata)
				newdata.parent = data
				newdata.display()
      else if msg.isScreenClosed() then
			  return -1
      end if
    end if
  end while
End Function

Function genericDisplay() As Integer
   print "Displaying"
   screen = m.preShowScreen()
	 return m.showScreen(screen)
End Function


Function preShowDetail(breadA=invalid, breadB=invalid) As Object
    port=CreateObject("roMessagePort")
    screen = CreateObject("roSpringboardScreen")
    screen.SetDescriptionStyle("video")
    screen.SetMessagePort(port)

    ' if breadA<>invalid and breadB<>invalid then
    '     screen.SetBreadcrumbText(breadA, breadB)
    ' end if

    return screen
End Function


Function showDetail(screen As Object) As Integer

    screen.ClearButtons()
    screen.AddButton(1, "resume playing")
    screen.AddButton(2, "play from beginning")

    screen.SetContent(m)
    screen.Show()

    'remote key id's for left/right navigation
    remoteKeyLeft  = 4
    remoteKeyRight = 5

    while true
        msg = wait(0, screen.GetMessagePort())

				showIndex = 0
        if type(msg) = "roSpringboardScreenEvent" then
            if msg.isScreenClosed()
                print "Screen closed"
                exit while
            else if msg.isRemoteKeyPressed()
                print "Remote key pressed"
                if msg.GetIndex() = remoteKeyLeft then
                        showIndex = getPrevShow(showList, showIndex)
                        if showIndex <> -1
                            refreshShowDetail(screen, showList, showIndex)
                        end if
                else if msg.GetIndex() = remoteKeyRight
                    showIndex = getNextShow(showList, showIndex)
                        if showIndex <> -1
                           refreshShowDetail(screen, showList, showIndex)
                        end if
												                endif
            else if msg.isButtonPressed()
                print "ButtonPressed"
                print "ButtonPressed"
                if msg.GetIndex() = 1
                    ' PlayStart = RegRead(showList[showIndex].ContentId)
										PlayStart = 0
                    ' if PlayStart <> invalid then
                    '    showList[showIndex].PlayStart = PlayStart.ToInt()
                    'endif
                    showVideoScreen(m)
                endif
                if msg.GetIndex() = 2
                    ' showList[showIndex].PlayStart = 0
                    showVideoScreen(m)
                endif
                if msg.GetIndex() = 3
                endif
                print "Button pressed: "; msg.GetIndex(); " " msg.GetData()
            end if
        else
            print "Unexpected message class: "; type(msg)
        end if
    end while

    return showIndex

End Function
