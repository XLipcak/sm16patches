# -*- coding: utf-8 -*-
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
from urlparse import urlparse


## Handler classes

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/home.html")

        ## PatchRequest only for testing purposes - to be deleted
        example = PatchRequest([{
            "instruction": "UPDATE",
            "changes": {
                "ADD": {
                    "subject": "http://dbpedia.org/page/Albert_Einstein",
                    "predicate": "http://xmls.com/foaf/0.1/accountName",
                    "value": {
                        "type": "literal",
                        "value": "123120194"
                    }
                },
                "DELETE": {
                    "subject": "http://dbpedia.org/page/Albert_Einstein",
                    "predicate": "http://xmls.com/foaf/0.1/accountName",
                    "value": {
                        "type": "literal",
                        "value": "123120194"
                    }
                }
            }},
            {
                "instruction": "DELETE",
                "subject": "http://dbpedia.org/page/Albert_Einstein",
                "predicate": "http://xmls.com/foaf/0.1/accountName",
                "value": {
                    "type": "literal",
                    "value": "123120194"
                }
            },
            {
                "instruction": "ADD",
                "subject": "http://dbpedia.org/page/Albert_Einstein",
                "predicate": "http://xmls.com/foaf/0.1/accountName",
                "value": {
                    "type": "literal",
                    "value": "123120194"
                }
            }])


class ResourceHandler(tornado.web.RequestHandler):
    def get(self):
        url = self.get_argument('url', '')
        searchText = self.get_argument('searchText', '')

        response = performGetRequest(url)
        graph = parseHttpResponseToGraph(response)
        msgs = buildMsgsFromGraph(graph)

        # jsonData = buildNaiveJsonFromGraph(graph)

        # graph = buildGraphFromJson(jsonData)

        if not searchText:
            self.render("templates/resource.html", rdfGraph=graph, url=url, searchText='')
        else:
            self.render("templates/resource.html", rdfGraph=self.filterRdfData(graph, searchText), url=url,
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


## Only one PatchRequestHandler is necessary, one of them to be deleted later
class PatchRequestHandler(tornado.web.RequestHandler):
    def get(self):
        patchJson = self.get_argument('patchJson', '')
        patchRequest = PatchRequest(patchJson)


class PatchRequestPostHandler(tornado.web.RequestHandler):
    def get(self):
        pass

    def post(self):
        patchJson = tornado.escape.json_decode(self.request.body)
        patchRequest = PatchRequest(patchJson)


## Patch requests functionality
## TODO: Think about moving this functionality to client, and add validation
class PatchRequest():
    # TODO Encapsulate patch instructions into separate class
    patchInstructionsList = []

    def __init__(self, patchRequestJson):
        patchRequestJson = patchRequestJson

        print("Processing patch request:")
        print(patchRequestJson)

        for patchInstructionJson in patchRequestJson:
            actualPatchInstructionString = patchInstructionJson.get('instruction')
            patchInstruction = {}

            patchInstruction['status'] = 'Open'
            patchInstruction['appliesTo'] = '-'
            patchInstruction['patchType'] = '-'
            patchInstruction['comment'] = '-'
            patchInstruction['memberOf'] = '-'

            patchInstruction['wasGeneratedBy'] = {}
            patchInstruction['wasGeneratedBy']['wasAssociatedWith'] = '-'
            patchInstruction['wasGeneratedBy']['confidence'] = '-'

            patchInstruction['update'] = {}

            if actualPatchInstructionString == 'UPDATE':
                patchUpdateInstructions = patchInstructionJson.get('changes')
                ##TODO Implement another solution of getting target graph
                patchInstruction['update']['target_graph'] = self.parseUrl(
                    patchUpdateInstructions.get('ADD').get('subject'))
                patchInstruction['update']['target_subject'] = patchUpdateInstructions.get('ADD').get('subject')
                patchInstruction['update']['insert'] = {
                    'predicate': patchUpdateInstructions.get('ADD').get('predicate'),
                    'object': patchUpdateInstructions.get('ADD').get('value').get('value')}
                patchInstruction['update']['delete'] = {
                    'predicate': patchUpdateInstructions.get('DELETE').get('predicate'),
                    'object': patchUpdateInstructions.get('DELETE').get('value').get('value')}

            elif actualPatchInstructionString == 'DELETE' or actualPatchInstructionString == 'ADD':
                patchInstruction['update']['target_graph'] = self.parseUrl(
                    patchUpdateInstructions.get(actualPatchInstructionString).get('subject'))
                patchInstruction['update']['target_subject'] = patchInstructionJson.get('subject')
                patchInstruction['update'][actualPatchInstructionString] = {
                    'predicate': patchInstructionJson.get('predicate'),
                    'object': patchInstructionJson.get('value').get('value')}

            self.patchInstructionsList.append(patchInstruction)

        print('Generated patch requests:')
        print(self.patchInstructionsList)

    def to_string(self):
        pass

    def parseUrl(self, url):
        parsedUrl = urlparse(url)
        return parsedUrl.scheme + '://' + parsedUrl.netloc + '/'


## convenience functions

def performGetRequest(url):
    opener = urllib2.build_opener()
    request = urllib2.Request(url)
    request.add_header('Accept',
                       'application/rdf+xml;q=0.9, text/n3, text/turtle, application/n-triples, application/ld+json')
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


def buildNaiveJsonFromGraph(graph):
    print("Start building navie JSON from graph...")
    start = time.time()

    jsonDict = {}
    for sub, pred, obj in graph:
        if sub not in jsonDict:
            jsonDict[sub] = {}
        jsonDict[sub][pred] = []
        if isinstance(obj, URIRef):
            jsonDict[sub][pred].append(
                {
                    "type": "uri",
                    "value": obj
                }
            )
        elif isinstance(obj, Literal):
            jsonDict[sub][pred].append(
                {
                    "type": "literal",
                    "value": obj
                }
            )
        else:
            jsonDict[sub][pred].append(
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
        URL(r"/patch_requests_post", PatchRequestPostHandler, name="patch_requests_post")
    ], debug=True, **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
