route = (handle, path, request, response) ->
	if typeof handle[path] == 'function'
		handle[path](request, response)
	else
		response.writeHead(404, {"Content-Type": "text/html;charset=UTF-8"})
		response.write("404 Not found")
		response.end()

exports.route = route
