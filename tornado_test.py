# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
from tornado.web import URLSpec as URL

import urllib2
import rdflib
import json
import os


## Handler classes

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("test_template.html")

class ResourceHandler(tornado.web.RequestHandler):
	def get(self):
		url = self.get_argument('url', '')
		rdfData = performGetRequest(url)
		rdfData = json.loads(rdfData)

		# writeToFile(rdfData, 'einstein.2json')

		self.render("rdf.html", rdfData = rdfData)

## convenience functions

def performGetRequest(url):
	opener = urllib2.build_opener()
	request = urllib2.Request(url)
	request.add_header('Accept', 'application/rdf+json')
	try:
		response = opener.open(request).read()
	except Exception, e:
		response = "not a valid url"
	return response

def writeToFile(data, fileName):
	file = open(fileName, 'w')
	file.write(data)
	file.close()

## Tornado setup

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}

def make_app():
	return tornado.web.Application([
		URL(r"/", MainHandler, name = "main"),
		URL(r"/rdf", ResourceHandler, name = "resource"),
	], debug = True, **settings)

if __name__ == "__main__":
	app = make_app()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()

