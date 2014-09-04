server = require './server'
router = require './router'
requestHandlers = require './requestHandlers'

handle = {}
handle['/'] = requestHandlers.index
handle['/index'] = requestHandlers.index
handle['/query'] = requestHandlers.query

port = 8000

server.start(router.route, handle, port)