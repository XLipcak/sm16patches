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

		self.render("rdf_graph.html", rdfGraph = graph, url = url, searchText = "")

		# if not searchText:
		# 	self.render("rdf.html", rdfData=rdfData, url=url, searchText='')
		# else:
		# 	self.render("rdf.html", rdfData=self.filterRdfData(rdfData, searchText), url=url, searchText=searchText)

	def filterRdfData(self, rdfData, searchText):
		filteredRdfData = {}
		for subject, predicateDict in rdfData.items():

			# subject recognized -> list this object with all its predicates and objects
			if subject.find(searchText) != -1:
				filteredRdfData[subject] = predicateDict

			else:
				filteredPredicates = {}
				for predicate, objectList in predicateDict.items():
					# predicate recognized -> list this predicate with all its objects
					if predicate.find(searchText) != -1:
						filteredPredicates[predicate] = objectList
					else:
						objects = []
						for objectDict in objectList:
							# object recognized -> list this object with its subject and predicate
							if unicode(objectDict["value"]).encode('ascii', 'ignore').decode('ascii').find(
									searchText) != -1:
								objects.append(objectDict)
						if len(objects) != 0:
							filteredPredicates[predicate] = objects
				if len(filteredPredicates) != 0:
					filteredRdfData[subject] = filteredPredicates

		return filteredRdfData

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

