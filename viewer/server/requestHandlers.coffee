MongoClient = require('mongodb').MongoClient

collection = null
MongoClient.connect "mongodb://localhost:27017/sybbs", (error, db) ->
	return console.dir(error) if error
	collection = db.collection('thread');

index = (request, response) ->
	response.writeHead(200, {'Content-Type': 'text/html;charset=UTF-8'})
	response.write('Hello index')
	response.end()

query = (request, response) ->
	if request.method != 'POST'
		response.writeHead(200, {'Content-Type': 'text/html;charset=UTF-8'})
		response.write('POST!')
		response.end()
	else
		postData = ''
		request.setEncoding 'utf8'
		request.addListener 'data', (chunk)->
			postData += chunk;

		request.addListener 'end', ->
			if postData?
				execQuery(JSON.parse(postData), response)
			else
				response.writeHead(200, {'Content-Type': 'text/html;charset=UTF-8'})
				response.write('Null post data')
				response.end()

	execQuery = (postData, response)->
		regexString = postData.join('|')

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