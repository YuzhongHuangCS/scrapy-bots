MongoClient = require('mongodb').MongoClient

collection = null
MongoClient.connect "mongodb://localhost:27017/sybbs", (error, db) ->
	if error
		console.dir(error)
		process.exit(1)
	else
		collection = db.collection('thread');

index = (request, response) ->
	response.writeHead(200, {'Content-Type': 'text/html;charset=UTF-8'})
	response.write('Hello index')
	response.end()

query = (request, response) ->
	if request.method != 'POST'
		response.writeHead(403, {'Content-Type': 'text/html;charset=UTF-8'})
		response.write('POST!')
		response.end()
	else
		postData = ''
		request.setEncoding 'utf8'
		request.addListener 'data', (chunk)->
			postData += chunk;

		request.addListener 'end', ->
			try
				execQuery(JSON.parse(postData).join('|'), response)
			catch exception
				response.writeHead(403, {'Content-Type': 'text/html;charset=UTF-8'})
				response.write('invalid post data')
				response.end()

	execQuery = (regexString, response)->
		collection.find({
			$or: [
				{title: {$regex: regexString}},
				{reply: {$regex: regexString}}
			]
		}).toArray (error, result)->
			if error
				response.writeHead(500, {'Content-Type': 'text/html;charset=UTF-8'})
				response.write(error)
				response.end()
			else
				response.writeHead(200, {'Content-Type': 'application/json;charset=UTF-8'})
				response.write(JSON.stringify(result))
				response.end()

exports.index = index
exports.query = query
