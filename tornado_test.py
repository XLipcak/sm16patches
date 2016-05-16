# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
from tornado.web import URLSpec as URL

import urllib2
## external dependencies: rdflib, rdflib-jsonld
from rdflib import Graph, plugin
from rdflib.serializer import Serializer
import json
import os


## Handler classes

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("test_template.html")

class ResourceHandler(tornado.web.RequestHandler):
	def get(self):
		url = self.get_argument('url', '')
		searchText = self.get_argument('searchText', '')

		response = performGetRequest(url)
		graph = parseHttpResponseToGraph(response)

		if not searchText:
			self.render("rdf_graph.html", rdfGraph=graph, url=url, searchText='')
		else:
			self.render("rdf_graph.html", rdfGraph=self.filterRdfData(graph, searchText), url=url, searchText=searchText)

	def filterRdfData(self, rdfGraph, searchText):
		filteredGraph = Graph()

		for s, p, o in rdfGraph:
			if searchText in s or searchText in o or searchText in p:
				filteredGraph.add( (s, p, o) )

		return filteredGraph


class PatchRequestHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("patch.html")

## convenience functions

def performGetRequest(url):
	opener = urllib2.build_opener()
	request = urllib2.Request(url)
	request.add_header('Accept', 'application/rdf+xml;q=0.9, text/n3, text/turtle, application/n-triples, application/ld+json')
	try:
		response = opener.open(request)
	except Exception, e:
		raise e
	return response

def parseHttpResponseToGraph(response):
	responseDict = dict(response.info())
	contentType = responseDict['content-type'][:-15]

	print("Detected content type: {}".format(contentType))

	contentTypeLookup = {
		'application/rdf+xml' : 'xml',
		'application/ld+json' : 'json-ld',
		'text/n3' : 'nt',
		'text/turtle' : 'turtle',
		'application/n-triples' : 'nt'
	}

	graph = Graph().parse(data=response.read(), format=contentTypeLookup[contentType])
	return graph


## if this method should be used ever again, refactor it to use "with open as file"
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
		URL(r"/patch_requests", PatchRequestHandler, name="patch_requests"),
	], debug = True, **settings)

if __name__ == "__main__":
	app = make_app()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()

