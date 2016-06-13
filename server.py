# -*- coding: utf-8 -*-
import datetime
import tornado.ioloop
import tornado.web
from tornado.web import URLSpec as URL

import urllib2
## external dependencies: rdflib, rdflib-jsonld
from rdflib import Graph, plugin, URIRef, Literal, BNode
from rdflib.serializer import Serializer
import json
import os
import time
from patches import PatchRequest, PatchRequestPersistence
from datetime import datetime


## Handler classes

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/home.html")


def storeGraphAsNTriples(graph, url):
    ## at the moment storing also works when just refreshing the page
    ## this shouldn't happen as we want to match stored resources to a user

    timestamp = str(datetime.now())[:-7]

    ## do regex matching in case of https
    ## the server doesn't seem to support https at the moment
    url = url[7:].replace("/", "")

    baseDirectory = "resource_cache"

    if not os.path.exists(baseDirectory):
        os.makedirs(baseDirectory)

    directory = baseDirectory + "/" + url

    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, timestamp.replace(':', '-'))
    print(filename)

    with open(filename, 'w') as outfile:
        outfile.write(graph.serialize(format="nt"))
    return filename

def loadNTriplesFromFile(url):
    url = url[7:].replace("/", "")
    path = "resource_cache/" + url

    currentDate = str(datetime.now())[:-7]
    currentDate = datetime.strptime(currentDate, "%Y-%m-%d %H:%M:%S")

    DAY_THRESHOLD = 7
    currentFile = None

    if os.path.isdir(path):
        for file in os.listdir(path):
            if file == ".DS_Store":
                continue
            date = datetime.strptime(file, '%Y-%m-%d %H-%M-%S')
            dateDifference = currentDate - date
            if dateDifference.days < DAY_THRESHOLD:
                currentFile = file
        if currentFile is not None:
            return Graph().parse(path + "/" + currentFile, format="nt"), currentFile
        else:
            return None
    else:
        return None

class ResourceHandler(tornado.web.RequestHandler):
    def get(self):
        url = self.get_argument('url', '')
        searchText = self.get_argument('searchText', '')

        graph, filename = loadNTriplesFromFile(url)

        if graph is None:
            print("no cached version found")
            resource = performGetRequest(url)
            graph = parseHttpResponseToGraph(resource)
            filename = storeGraphAsNTriples(graph, url)
            graph.parse(filename, format="nt")

        jsonData = buildNaiveJsonFromGraph(graph, url, filename)

        if not searchText:
            self.render("templates/resource.html", jsonData=jsonData, rdfGraph=graph, url=url, searchText='')
        else:
            self.render("templates/resource.html", jsonData=jsonData, rdfGraph=self.filterRdfData(graph, searchText), url=url,
                        searchText=searchText)

    def filterRdfData(self, rdfGraph, searchText):
        filteredGraph = Graph()

        searchText = searchText.lower()

        for s, p, o in rdfGraph:
            if searchText in s or searchText in o or searchText in p:
                filteredGraph.add((s, p, o))

        return filteredGraph

class PatchListHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/patch.html")

class PatchRequestHandler(tornado.web.RequestHandler):
    def get(self):
        pass

    def post(self):
        ## TODO: match request against a cached resource
        ## if match: generate patch
        ## if no match: reject the request

        patchRequestJson = tornado.escape.json_decode(self.request.body)
        print(patchRequestJson["url"])
        print(patchRequestJson["filename"])
        patchRequestPersistence = PatchRequestPersistence('patch_request_storage')
        patchRequestPersistence.save(patchRequestJson)

def performGetRequest(url):
    ## try to find out 'last modified' of the resource
    ## if there are no changes, use the serialized version instead of performing another get request
    opener = urllib2.build_opener()
    request = urllib2.Request(url)
    request.add_header('Accept','application/rdf+xml;q=0.9, text/n3, text/turtle, application/n-triples, application/ld+json')

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
        'application/rdf+xml': 'xml',
        'application/ld+json': 'json-ld',
        'text/n3': 'nt',
        'text/turtle': 'turtle',
        'application/n-triples': 'nt'
    }

    graph = Graph().parse(data=response.read(), format=contentTypeLookup[contentType])
    return graph


## This method works, but is currently taking way to long due to the graph not keeping triples in order
def buildJsonFromGraph(graph):
    print("Start building JSON from graph...")
    start = time.time()

    jsonDict = {}
    for sub, pred, obj in graph:
        jsonDict[sub] = {}
        for sub2, pred2, obj2 in graph.triples((sub, None, None)):
            jsonDict[sub][pred2] = []
            for sub3, pred3, obj3 in graph.triples((sub, pred2, None)):
                if isinstance(obj3, URIRef):
                    jsonDict[sub][pred2].append(
                        {
                            "type": "uri",
                            "value": obj3
                        }
                    )
                elif isinstance(obj3, Literal):
                    jsonDict[sub][pred2].append(
                        {
                            "type": "literal",
                            "value": obj3
                        }
                    )
                else:
                    jsonDict[sub][pred2].append(
                        {
                            "type": "bnode",
                            "value": obj3
                        }
                    )
    jsonData = json.dumps(jsonDict)

    duration = time.time() - start
    print("Took {} seconds".format(duration))

    return jsonData


def buildNaiveJsonFromGraph(graph, url, filename):
    print("Start building navie JSON from graph...")
    start = time.time()

    jsonDict = {}
    jsonDict["filename"] = filename
    jsonDict["url"] = url
    jsonDict["data"] = {}

    for sub, pred, obj in graph:
        if sub not in jsonDict["data"]:
            jsonDict["data"][sub] = {}
        jsonDict["data"][sub][pred] = []
        if isinstance(obj, URIRef):
            jsonDict["data"][sub][pred].append(
                {
                    "type": "uri",
                    "value": obj
                }
            )
        elif isinstance(obj, Literal):
            jsonDict["data"][sub][pred].append(
                {
                    "type": "literal",
                    "value": obj
                }
            )
        else:
            jsonDict["data"][sub][pred].append(
                {
                    "type": "bnode",
                    "value": obj
                }
            )

    jsonData = json.dumps(jsonDict)

    duration = time.time() - start
    print("Took {} seconds".format(duration))

    return jsonData


def buildGraphFromJson(jsonData):
    graph = Graph()
    jsonDict = json.loads(jsonData)

    for sub, predDict in jsonDict.items():
        subToPut = None
        if sub.startswith("http"):
            subToPut = URIRef(sub.encode("utf-8"))
        else:
            subToPut = BNode(sub.encode("utf-8"))
        for pred, objDictList in predDict.items():
            for objDict in objDictList:
                if objDict["type"] == "literal" or objDict["value"] == "*":
                    print("{} {} {} ({})".format(subToPut, pred, objDict["value"].encode("utf-8"), objDict["type"]))
                    graph.add((subToPut, URIRef(pred), Literal(objDict["value"].encode("utf-8"))))
                elif objDict["type"] == "uri":
                    print("{} {} {}".format(subToPut.encode('utf-8'), pred, objDict["value"].encode('utf-8')))
                    graph.add((subToPut, URIRef(pred), URIRef(objDict["value"].encode("utf-8"))))
                else:
                    print("{} {} {}".format(subToPut, pred, objDict["value"].encode("utf-8")))
                    graph.add((subToPut, URIRef(pred), BNode(objDict["value"].encode("utf-8"))))

    return graph


def writeToFile(data, fileName):
    with open(fileName, 'w') as outfile:
        outfile.write(data)


def buildMsgsFromGraph(graph):
    msgs = {}
    bnodeLookup = {}

    splitGraphIntoMsgs(graph, msgs, bnodeLookup)
    mergeMsgs(msgs, bnodeLookup)

    for msg in [x for x in msgs.values() if not x['final']]:
        print(msg)
    for msg in [x for x in msgs.values() if x['final']]:
        print(msg)

    return msgs


def splitGraphIntoMsgs(graph, msgs, bnodeLookup):
    msgId = 0
    for s, p, o in graph:
        msg = {
            'triples': set([(s, p, o)]),
            'bnodeIds': set(),
            'final': True
        }
        if isinstance(s, BNode):
            if s not in bnodeLookup:
                bnodeLookup[s] = []
            bnodeLookup[s].append(msgId)
            msg['bnodeIds'].add(s)
            msg['final'] = False
        if isinstance(o, BNode):
            if o not in bnodeLookup:
                bnodeLookup[o] = []
            bnodeLookup[o].append(msgId)
            msg['bnodeIds'].add(o)
            msg['final'] = False
        msgs[msgId] = msg
        msgId += 1


def mergeMsgs(msgs, bnodeLookup):
    removableMsgsById = set()

    for msg in msgs.values():
        if msg['final']:
            continue
        for bnodeId in msg['bnodeIds']:
            for msgId in bnodeLookup[bnodeId]:
                if msg == msgs[msgId]:
                    continue
                for triple in msgs[msgId]['triples']:
                    msg['triples'].add(triple)
                for bnodeId in msgs[msgId]['bnodeIds']:
                    msg['bnodeIds'].add(bnodeId)
                msgs[msgId]['final'] = True
                removableMsgsById.add(msgId)

    for msgId in removableMsgsById:
        del (msgs[msgId])


## Tornado setup

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}


def make_app():
    return tornado.web.Application([
        URL(r"/", MainHandler, name="main"),
        URL(r"/resource", ResourceHandler, name="resource"),
        URL(r"/patch_list", PatchListHandler, name="patch_list"),
        URL(r"/patch_requests", PatchRequestHandler, name="patch_requests"),
    ], debug=True, **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("start server...")
    tornado.ioloop.IOLoop.current().start()
