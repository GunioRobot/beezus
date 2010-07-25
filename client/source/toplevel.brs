
Function makeTopLevel() as Object

		top = makeGenericList("toplevel")

		top.posterStyle = "flat-category"

		top.nextLoader = loadCategory

		' Add the 'configuration'
		config = makeConfiguration()
		top.config = config

		' The 'tv' category
		top.values.Push(makeTVCategory(config))

		' The 'movies' category
		top.values.Push(makeMoviesCategory(config))

		' Adding in the configuration
		top.values.Push(makeConfigCategory(config))

		return top
End Function


' Currently the 'nextLoader' takes, as an argument, the object to load. We
' should use this to update the top-level category, so that it doesn't the
'category each time. We should copy the results into the arguments, and update
' the 'nextLoader' to simply return the object. However we're not doing that
' quite yet.
Function loadCategory(category as Object) as Object
   o =  category.catLoader()
	 return o
End Function

Function makeTVCategory(config as Object) as Object
  o = makeGenericList("category")
	o.catLoader = loadTV
	o.Title = "TV"
	o.ShortDescriptionLine1 = "TV"
	o.HDPosterURL = "pkg://images/category/tv.png"
	o.config = config

	return o
End Function

Function makeMoviesCategory(config as Object) as Object
  o = makeGenericList("category")
	o.catLoader = loadMovies
	o.Title = "Movies"
	o.ShortDescriptionLine1 = "Movies"
	o.HDPosterURL = "pkg://images/category/movies.png"

	o.nextLoader = loadMovie
	o.config = config
	return o
End Function

Function makeConfigCategory(config as Object) as Object
  o = makeGenericList("category")

	' The logic for the configuration is completely different from that of the
  ' browser categories, but we'll not handle that now.
	o.catLoader = configLoader

	o.Title = "Configuration"
	o.ShortDescriptionLine1 = "Configure"
	o.HDPosterURL = "pkg://images/category/config.png"
	o.config = config

	o.preShowScreen = configPreShowScreen
	o.showScreen = configShowScreen

	return o

End Function

Function configLoader() as Object
  return m
End Function