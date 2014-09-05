http = require 'http'
url = require 'url'

start = (route, handle, port) ->
	onRequest = (request, response) ->
		path = url.parse(request.url).path	
		route(handle, path, request, response)

	http.createServer(onRequest).listen(port)
	console.log "Server has started @#{port}."
  
exports.start = start
